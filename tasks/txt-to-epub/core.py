import os
import logging
import chardet
from typing import Optional, Dict, Any
from ebooklib import epub

from .data_structures import Volume
from .parser import parse_hierarchical_content
from .css import add_css_style
from .html_generator import create_volume_page, create_chapter_page, create_section_page, create_chapter
from .word_count_validator import validate_conversion_integrity

# Configure logging
logger = logging.getLogger(__name__)


def _create_epub_book(title: str, author: str, cover_image: Optional[str] = None) -> epub.EpubBook:
    """Create a new EPUB book and set metadata."""
    book = epub.EpubBook()
    book.set_title(title)
    book.set_language('zh')  # Set language to Chinese
    book.add_author(author)

    if cover_image:
        _set_cover_image(book, cover_image)

    return book


def _set_cover_image(book: epub.EpubBook, cover_image: str) -> None:
    """Set the cover image for the book."""
    try:
        with open(cover_image, 'rb') as cover_file:
            book.set_cover('cover.png', cover_file.read())
    except IOError as e:
        logger.error(f"Unable to read cover image {cover_image}: {e}")


def _read_txt_file(txt_file: str) -> str:
    """Read text file content with automatic encoding detection."""
    try:
        # Check if file exists
        if not os.path.exists(txt_file):
            raise FileNotFoundError(f"File does not exist: {txt_file}")
        
        # Check file size
        file_size = os.path.getsize(txt_file)
        if file_size == 0:
            logger.warning(f"File is empty: {txt_file}")
            return "This document is empty."
        
        # Detect file encoding
        with open(txt_file, 'rb') as f:
            # Read sufficient data for encoding detection, but not exceeding 1MB
            sample_size = min(file_size, 1024 * 1024)
            raw_data = f.read(sample_size)
            result = chardet.detect(raw_data)
            encoding = result.get('encoding') or 'gb18030'
            confidence = result.get('confidence', 0)
            
            logger.info(f"Detected file encoding: {encoding} (confidence: {confidence:.2f})")

        # Use GB18030 encoding to handle Chinese encoding issues
        if encoding and encoding.lower() in ['gb2312', 'gbk']:
            encoding = 'gb18030'
        
        # Try multiple encodings to read file
        encodings_to_try = [encoding, 'utf-8', 'gb18030', 'gbk', 'utf-16', 'latin1']
        
        for enc in encodings_to_try:
            if not enc:
                continue
            try:
                with open(txt_file, 'r', encoding=enc, errors='replace') as f:
                    content = f.read()
                    # Verify content is reasonable (not all replacement characters)
                    if content and content.count('�') / len(content) < 0.1:  # Less than 10% replacement characters
                        logger.info(f"Successfully read file using encoding {enc}")
                        return content
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # If all encodings fail, use final fallback option
        logger.warning(f"All encoding attempts failed, using fallback to read file: {txt_file}")
        with open(txt_file, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
            
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except IOError as e:
        raise IOError(f"Unable to read file {txt_file}: {e}")
    except Exception as e:
        raise Exception(f"Error occurred while reading file {txt_file}: {e}")


def _write_epub_file(epub_file: str, book: epub.EpubBook) -> None:
    """Write EPUB file."""
    try:
        epub.write_epub(epub_file, book, {})
        logger.info(f"Successfully generated EPUB file: {epub_file}")
    except Exception as e:
        raise Exception(f"Unable to write EPUB file {epub_file}: {e}")


def txt_to_epub(txt_file: str, epub_file: str, title: str = 'My Book', 
                author: str = 'Unknown', cover_image: Optional[str] = None) -> Dict[str, Any]:
    """
    Convert text file to EPUB format e-book, supports Chinese content.

    :param txt_file: Input text file path
    :param epub_file: Output EPUB file path
    :param title: Book title
    :param author: Author name
    :param cover_image: Cover image path (optional)
    """
    # Validate input parameters
    if not txt_file or not txt_file.strip():
        raise ValueError("Input file path cannot be empty")
    
    if not epub_file or not epub_file.strip():
        raise ValueError("Output file path cannot be empty")
    
    if not txt_file.lower().endswith('.txt'):
        raise ValueError("Input file must be .txt format")
    
    if not epub_file.lower().endswith('.epub'):
        raise ValueError("Output file must be .epub format")

    logger.info(f"Starting conversion: {txt_file} -> {epub_file}")
    
    try:
        # Create EPUB book
        book = _create_epub_book(title, author, cover_image)
        
        # Read and analyze text content
        content = _read_txt_file(txt_file)
        
        # Verify content is not empty
        if not content or not content.strip():
            logger.warning("File content is empty, creating default content")
            content = "This document content is empty or cannot be parsed."
        
        logger.info(f"File content length: {len(content)} characters")
        
        volumes = parse_hierarchical_content(content)
        
        # Validate parsing results
        if not volumes:
            logger.error("Parsing failed, no volumes generated")
            raise Exception("Document parsing failed, unable to generate EPUB")
        
        logger.info(f"Parsing completed, generated {len(volumes)} volumes")

        # Add volumes, chapters and sections to book
        chapter_items = []
        toc_structure = []
        chapter_counter = 1
        volume_counter = 1
        
        for volume in volumes:
            if volume.title:  # If has volume title
                # Create a page for the volume
                volume_file_name = f"volume_{volume_counter}.xhtml"
                volume_page = create_volume_page(volume.title, volume_file_name, len(volume.chapters))
                book.add_item(volume_page)
                chapter_items.append(volume_page)
                
                # Create volume table of contents link (top level, not indented)
                volume_link = epub.Link(volume_file_name, volume.title, f"volume_{volume_counter}")
                volume_chapters = []
                
                for chapter in volume.chapters:
                    if chapter.sections:  # Chapter has sections
                        # Create chapter page
                        chapter_file_name = f"chap_{chapter_counter}.xhtml"
                        chapter_page = create_chapter_page(chapter.title, chapter.content, chapter_file_name, len(chapter.sections))
                        book.add_item(chapter_page)
                        chapter_items.append(chapter_page)
                        
                        # Create chapter table of contents link (indented one level relative to volume)
                        chapter_link = epub.Link(chapter_file_name, chapter.title, f"chap_{chapter_counter}")
                        section_links = []
                        section_counter = 1
                        
                        # Handle sections under chapter
                        for section in chapter.sections:
                            section_file_name = f"chap_{chapter_counter}_sec_{section_counter}.xhtml"
                            section_page = create_section_page(section.title, section.content, section_file_name)
                            book.add_item(section_page)
                            chapter_items.append(section_page)
                            # Create section table of contents link (indented one more level relative to chapter)
                            section_links.append(epub.Link(section_file_name, section.title, f"chap_{chapter_counter}_sec_{section_counter}"))
                            section_counter += 1
                        
                        # Add chapter and its sections as nested structure
                        volume_chapters.append((chapter_link, section_links))
                    else:  # Chapter has no sections, add chapter content directly
                        chapter_page = create_chapter(chapter.title, chapter.content, f"chap_{chapter_counter}.xhtml")
                        book.add_item(chapter_page)
                        chapter_items.append(chapter_page)
                        # Chapter directly as volume sub-item (indented one level relative to volume)
                        volume_chapters.append(epub.Link(f"chap_{chapter_counter}.xhtml", chapter.title, f"chap_{chapter_counter}"))
                    
                    chapter_counter += 1
                
                # Add volume to table of contents structure: volume title + hierarchical structure of chapters and sections below it
                toc_structure.append((volume_link, volume_chapters))
                volume_counter += 1
            else:  # No volumes, add chapters directly
                for chapter in volume.chapters:
                    if chapter.sections:  # Chapter has sections
                        # Create chapter page
                        chapter_file_name = f"chap_{chapter_counter}.xhtml"
                        chapter_page = create_chapter_page(chapter.title, chapter.content, chapter_file_name, len(chapter.sections))
                        book.add_item(chapter_page)
                        chapter_items.append(chapter_page)
                        
                        # Create chapter table of contents link (top level)
                        chapter_link = epub.Link(chapter_file_name, chapter.title, f"chap_{chapter_counter}")
                        section_links = []
                        section_counter = 1
                        
                        # Handle sections under chapter
                        for section in chapter.sections:
                            section_file_name = f"chap_{chapter_counter}_sec_{section_counter}.xhtml"
                            section_page = create_section_page(section.title, section.content, section_file_name)
                            book.add_item(section_page)
                            chapter_items.append(section_page)
                            # Create section table of contents link (indented one level relative to chapter)
                            section_links.append(epub.Link(section_file_name, section.title, f"chap_{chapter_counter}_sec_{section_counter}"))
                            section_counter += 1
                        
                        # Add chapter and its sections as nested structure
                        toc_structure.append((chapter_link, section_links))
                    else:  # Chapter has no sections, add chapter content directly
                        chapter_page = create_chapter(chapter.title, chapter.content, f"chap_{chapter_counter}.xhtml")
                        book.add_item(chapter_page)
                        chapter_items.append(chapter_page)
                        # Chapter as top-level item
                        toc_structure.append(epub.Link(f"chap_{chapter_counter}.xhtml", chapter.title, f"chap_{chapter_counter}"))
                    
                    chapter_counter += 1

        # Set book structure
        book.toc = toc_structure
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Add style and set spine
        add_css_style(book)
        book.spine = ['nav'] + chapter_items

        # Ensure output directory exists and write file
        os.makedirs(os.path.dirname(epub_file), exist_ok=True)
        _write_epub_file(epub_file, book)
        
        # Verify conversion content integrity
        logger.info("Starting conversion content integrity verification...")
        is_valid, validation_report = validate_conversion_integrity(content, volumes)
        
        # Output verification report
        print("\n" + validation_report)
        
        if not is_valid:
            logger.warning("Content integrity verification failed, possible content loss")
        else:
            logger.info("Content integrity verification passed, good conversion quality")
        
        logger.info(f"EPUB conversion completed: {epub_file}")
        
        return {
            "success": True,
            "output_file": epub_file,
            "validation_passed": is_valid,
            "validation_report": validation_report,
            "volumes_count": len(volumes),
            "chapters_count": sum(len(volume.chapters) for volume in volumes)
        }
        
    except Exception as e:
        logger.error(f"Error occurred during conversion: {e}")
        raise Exception(f"EPUB conversion failed: {e}")
