import re
import logging
from typing import List, Optional
from data_structures import Section, Chapter, Volume
from parser_config import ParserConfig, DEFAULT_CONFIG

# Configure logging
logger = logging.getLogger(__name__)


class ChinesePatterns:
    """Regular expression patterns for Chinese books"""
    
    # Table of contents keywords
    TOC_KEYWORDS = ["目录"]
    
    # Preface keywords
    PREFACE_KEYWORDS = ["前言", "序", "序言"]
    
    # Volume/Part/Book patterns
    VOLUME_PATTERN = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})[卷部篇]\s+[^\n]*)')
    
    # Chapter patterns
    CHAPTER_PATTERN = re.compile(r'(?:^|\n)(\s*(?:第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s+[^\n]+|(?:番外|番外篇|外传|特别篇|插话|后记|尾声|终章|楔子|序章)\s+[^\n]*)\s*)(?=\n|$)', re.MULTILINE)
    
    # Section patterns
    SECTION_PATTERN = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})节\s+[^\n]*)')


class EnglishPatterns:
    """Regular expression patterns for English books"""
    
    # Table of contents keywords
    TOC_KEYWORDS = ["Contents", "Table of Contents", "TOC"]
    
    # Preface keywords  
    PREFACE_KEYWORDS = ["Preface", "Foreword", "Introduction", "Prologue"]
    
    # Word to number mapping
    WORD_TO_NUM = {
        'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
        'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
        'eleven': '11', 'twelve': '12', 'thirteen': '13', 'fourteen': '14', 'fifteen': '15',
        'sixteen': '16', 'seventeen': '17', 'eighteen': '18', 'nineteen': '19', 'twenty': '20'
    }
    
    # Roman numeral mapping
    ROMAN_TO_NUM = {
        'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5',
        'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10',
        'XI': '11', 'XII': '12', 'XIII': '13', 'XIV': '14', 'XV': '15',
        'XVI': '16', 'XVII': '17', 'XVIII': '18', 'XIX': '19', 'XX': '20'
    }
    
    # Volume/Part/Book patterns
    VOLUME_PATTERN = re.compile(r'(?:^|\n)(\s*(?:(?:Part|Book|Volume)\s+(?:I{1,3}V?|VI{0,3}|IX|X{1,2}|\d{1,2}|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|Seventeen|Eighteen|Nineteen|Twenty)(?::\s*[^\n]+)?)\s*)(?=\n|$)', re.MULTILINE | re.IGNORECASE)
    
    # Chapter patterns
    CHAPTER_PATTERN = re.compile(r'(?:^|\n)(\s*(?:Chapter|Ch\.?|Chap\.?)\s+(?:I{1,3}V?|VI{0,3}|IX|X{1,2}L?|\d{1,2}|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|Seventeen|Eighteen|Nineteen|Twenty|Thirty|Forty|Fifty)(?::\s*[^\n]+)?\s*)(?=\n|$)', re.MULTILINE | re.IGNORECASE)
    
    # Section patterns
    SECTION_PATTERN = re.compile(r'(?:^|\n)(\s*(?:Section|Sect\.?)\s+(?:\d{1,2}(?:\.\d+)?|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|Seventeen|Eighteen|Nineteen|Twenty)(?::\s*[^\n]+)?\s*)(?=\n|$)', re.MULTILINE | re.IGNORECASE)
    
    # Numbered section patterns (e.g., 1.1, 2.3)
    NUMBERED_SECTION_PATTERN = re.compile(r'(?:^|\n)(\s*(\d+\.\d+)\s+[^\n]+\s*)(?=\n|$)', re.MULTILINE)


def detect_language(content: str) -> str:
    """
    Detect the main language of the text (Chinese or English)

    :param content: Text content
    :return: 'chinese' or 'english'
    """
    if not content or not content.strip():
        return 'chinese'  # Default to Chinese

    # Count Chinese characters
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    # Count English letters
    english_chars = len(re.findall(r'[a-zA-Z]', content))

    # Check common Chinese chapter keywords
    chinese_keywords = ['第', '章', '节', '卷', '部', '篇', '序言', '前言', '目录']
    chinese_keyword_count = sum(content.count(kw) for kw in chinese_keywords)

    # Check common English chapter keywords
    english_keywords = ['Chapter', 'Section', 'Part', 'Book', 'Volume', 'Contents', 'Preface', 'Introduction']
    english_keyword_count = sum(content.lower().count(kw.lower()) for kw in english_keywords)

    # Decision logic
    if chinese_chars > english_chars * 0.5 or chinese_keyword_count > english_keyword_count:
        return 'chinese'
    else:
        return 'english'


def is_valid_chapter_title(match, content: str, language: str = 'chinese') -> bool:
    """
    Validate if a regex match is a genuine chapter title, not an inline reference.

    :param match: Regex match object
    :param content: Full text content
    :param language: Language type, 'chinese' or 'english'
    :return: True if valid chapter title, False if likely a reference
    """
    match_text = match.group(0).strip()
    match_start = match.start()
    match_end = match.end()

    # 1. Check if title is too long (likely not a real chapter title)
    if len(match_text) > 100:
        logger.debug(f"Rejected chapter title (too long): {match_text[:50]}...")
        return False

    # 2. Check context before the match
    context_before_start = max(0, match_start - 50)
    context_before = content[context_before_start:match_start]

    # Check if it's in the middle of a sentence (preceded by comma, etc.)
    if language == 'chinese':
        # Chinese: check for patterns like "在第X章", "如第X章", "见第X章"
        if re.search(r'[在如见到自从正前后于从到至]第.{0,5}章', context_before[-20:] + match_text[:10]):
            logger.debug(f"Rejected chapter title (inline reference): {match_text}")
            return False

        # Check if preceded by punctuation that suggests inline reference
        if re.search(r'[，,、；;]第.{0,5}章', context_before[-10:] + match_text[:10]):
            logger.debug(f"Rejected chapter title (after punctuation): {match_text}")
            return False
    else:
        # English: check for patterns like "in Chapter X", "see Chapter X"
        if re.search(r'(?:in|see|from|at|to|of|for)\s+Chapter\s+\w+', context_before[-30:] + match_text[:20], re.IGNORECASE):
            logger.debug(f"Rejected chapter title (inline reference): {match_text}")
            return False

    # 3. Check context after the match
    context_after_end = min(len(content), match_end + 50)
    context_after = content[match_end:context_after_end]

    if language == 'chinese':
        # Check for continuation phrases like "结束时", "中", "里"
        if re.match(r'^\s*[结结束时中里]', context_after):
            logger.debug(f"Rejected chapter title (continuation): {match_text}")
            return False

        # Check if followed by comma (inline reference pattern)
        if re.match(r'^\s*[，,]', context_after):
            logger.debug(f"Rejected chapter title (followed by comma): {match_text}")
            return False
    else:
        # English: check for continuation like "ends", "of the book"
        if re.match(r'^\s*(?:ends?|of|in|at)\s', context_after, re.IGNORECASE):
            logger.debug(f"Rejected chapter title (continuation): {match_text}")
            return False

    # 4. Check if the match is at the beginning of a line (real chapter titles usually are)
    # Allow some whitespace before the match
    line_start = content.rfind('\n', 0, match_start)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1

    text_before_match = content[line_start:match_start]
    if text_before_match.strip():  # Non-whitespace characters before match on same line
        # There's text before the chapter marker on the same line
        # This suggests it's not a standalone chapter title
        logger.debug(f"Rejected chapter title (not at line start): {match_text}")
        return False

    return True


def remove_table_of_contents(content: str, language: str = None) -> str:
    """
    Remove the table of contents section from the text to avoid interference with chapter recognition.
    Supports both Chinese and English table of contents recognition.
    
    :param content: Original text content
    :param language: Language type, 'chinese' or 'english', auto-detect if None
    :return: Text content with table of contents removed
    """
    if not content or not content.strip():
        return content
    
    # Auto-detect language
    if language is None:
        language = detect_language(content)
    
    # Select corresponding patterns
    if language == 'english':
        patterns = EnglishPatterns()
        toc_keywords = patterns.TOC_KEYWORDS
        preface_keywords = patterns.PREFACE_KEYWORDS
        chapter_patterns = [patterns.CHAPTER_PATTERN, patterns.VOLUME_PATTERN]
    else:
        patterns = ChinesePatterns()
        toc_keywords = patterns.TOC_KEYWORDS
        preface_keywords = patterns.PREFACE_KEYWORDS
        chapter_patterns = [patterns.CHAPTER_PATTERN, patterns.VOLUME_PATTERN]
    
    lines = content.split('\n')
    
    # Find table of contents start position
    toc_start = -1
    toc_end = -1
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        # Identify table of contents start: standalone line with TOC keywords
        if stripped_line in toc_keywords or any(keyword.lower() == stripped_line.lower() for keyword in toc_keywords):
            toc_start = i
            continue
            
        # If table of contents start found, look for the end
        if toc_start != -1:
            # Table of contents end conditions:
            # 1. Consecutive empty lines (usually TOC is followed by empty lines)
            # 2. Clear main content (long paragraphs)
            if not stripped_line:  # Empty line
                # Check if there are consecutive empty lines or main content following
                next_non_empty = -1
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip():
                        next_non_empty = j
                        break
                        
                if next_non_empty != -1:
                    next_line = lines[next_non_empty].strip()
                    # If next non-empty line is main content (long and not chapter title format)
                    if len(next_line) > 30:
                        is_chapter = False
                        for pattern in chapter_patterns:
                            if pattern.search(next_line):
                                is_chapter = True
                                break
                        if not is_chapter:
                            toc_end = i
                            break
            
            # If current line is clearly the beginning of main content (long paragraph)
            elif len(stripped_line) > 50:
                is_chapter = False
                is_preface = False
                
                # Check if it's a chapter title
                for pattern in chapter_patterns:
                    if pattern.search(stripped_line):
                        is_chapter = True
                        break
                
                # Check if it's a preface
                if any(keyword.lower() == stripped_line.lower() for keyword in preface_keywords):
                    is_preface = True
                
                if not is_chapter and not is_preface:
                    toc_end = i - 1
                    break
    
    # If table of contents found, remove it
    if toc_start != -1 and toc_end != -1:
        # Remove table of contents but keep content before and after
        remaining_lines = lines[:toc_start] + lines[toc_end + 1:]
        return '\n'.join(remaining_lines)
    elif toc_start != -1:
        # Only found table of contents start, possibly continues until clear chapter beginning
        for i in range(toc_start + 1, len(lines)):
            line = lines[i].strip()
            # Find first clear main content chapter title or preface
            for pattern in chapter_patterns:
                if pattern.search(line):
                    remaining_lines = lines[:toc_start] + lines[i:]
                    return '\n'.join(remaining_lines)
            if any(keyword.lower() == line.lower() for keyword in preface_keywords):
                remaining_lines = lines[:toc_start] + lines[i:]
                return '\n'.join(remaining_lines)
    
    return content


def parse_hierarchical_content(content: str, config: Optional[ParserConfig] = None) -> List[Volume]:
    """
    Split text content into three-level hierarchical structure: volumes, chapters, sections.
    Supports both Chinese and English book formats.
    Optimized version using finditer() for better performance.

    :param content: Text content
    :param config: Parser configuration (optional, uses default if None)
    :return: List of volumes containing complete hierarchical structure
    """
    if config is None:
        config = DEFAULT_CONFIG

    if not content or not content.strip():
        # If content is empty, return a volume with empty chapter
        return [Volume(title=None, chapters=[Chapter(title="Empty Content", content="This document is empty or cannot be parsed.", sections=[])])]

    # Detect language
    language = detect_language(content)

    # Preprocessing: remove table of contents to avoid interference with content parsing
    content = remove_table_of_contents(content, language)

    # Select corresponding patterns based on language
    if language == 'english':
        patterns = EnglishPatterns()
        volume_pattern = patterns.VOLUME_PATTERN
    else:
        patterns = ChinesePatterns()
        volume_pattern = patterns.VOLUME_PATTERN

    # Optimized: Use finditer() instead of split() for better performance
    volume_matches = list(volume_pattern.finditer(content))

    volumes = []

    if not volume_matches:
        # No volumes, only chapters
        chapters = parse_chapters_from_content(content, language, config)
        # Validate and merge short chapters if enabled
        if config.enable_length_validation:
            chapters = validate_and_merge_chapters(chapters, language, config.min_chapter_length)
        if chapters:
            volumes.append(Volume(title=None, chapters=chapters))
        else:
            # If no chapters detected, treat entire content as one chapter
            default_title = "正文" if language == 'chinese' else "Content"
            volumes.append(Volume(title=None, chapters=[Chapter(title=default_title, content=content.strip(), sections=[])]))
    else:
        # Handle first part (possibly preface, content without volume title)
        first_volume_start = volume_matches[0].start()
        if first_volume_start > 0 and content[:first_volume_start].strip():
            pre_content = content[:first_volume_start]
            pre_chapters = parse_chapters_from_content(pre_content, language, config)
            # Validate and merge short chapters if enabled
            if config.enable_length_validation:
                pre_chapters = validate_and_merge_chapters(pre_chapters, language, config.min_chapter_length)
            if pre_chapters:
                volumes.append(Volume(title=None, chapters=pre_chapters))
            else:
                # If first part has no chapter structure, treat as preface chapter
                preface_title = "序言" if language == 'chinese' else "Preface"
                volumes.append(Volume(title=None, chapters=[Chapter(title=preface_title, content=pre_content.strip(), sections=[])]))

        # Handle parts with volume titles
        seen_volume_titles = set()  # Track seen volume titles
        for i, match in enumerate(volume_matches):
            volume_title = match.group(1).strip()

            # Get volume content (from end of current match to start of next match, or end of text)
            volume_start = match.end()
            volume_end = volume_matches[i + 1].start() if i + 1 < len(volume_matches) else len(content)
            volume_content = content[volume_start:volume_end]

            # Check for duplicate volume titles, skip if duplicate
            if volume_title and volume_title not in seen_volume_titles:
                seen_volume_titles.add(volume_title)
                chapters = parse_chapters_from_content(volume_content, language, config)
                # Validate and merge short chapters if enabled
                if config.enable_length_validation:
                    chapters = validate_and_merge_chapters(chapters, language, config.min_chapter_length)
                if chapters:
                    volumes.append(Volume(title=volume_title, chapters=chapters))
                elif volume_content.strip():  # If has content but no chapter structure
                    # Treat entire volume content as one chapter
                    default_title = "正文" if language == 'chinese' else "Content"
                    volumes.append(Volume(title=volume_title, chapters=[Chapter(title=default_title, content=volume_content.strip(), sections=[])]))

    # Ensure at least one volume
    if not volumes:
        error_title = "未知内容" if language == 'chinese' else "Unknown Content"
        error_content = "无法解析文档结构，请检查文档格式。" if language == 'chinese' else "Unable to parse document structure. Please check document format."
        volumes.append(Volume(title=None, chapters=[Chapter(title=error_title, content=error_content, sections=[])]))

    return volumes


def parse_chapters_from_content(content: str, language: str = 'chinese', config: Optional[ParserConfig] = None) -> List[Chapter]:
    """
    Split chapters and sections from given content.
    Supports both Chinese and English chapter formats.
    Optimized version using finditer() for better performance.
    Validates chapter titles to filter out inline references.

    :param content: Text content
    :param language: Language type, 'chinese' or 'english'
    :param config: Parser configuration (optional)
    :return: Chapter list, each chapter contains title, content and section list
    """
    if config is None:
        config = DEFAULT_CONFIG

    if not content or not content.strip():
        return []

    # Select corresponding patterns based on language
    if language == 'english':
        patterns = EnglishPatterns()
        chapter_pattern = patterns.CHAPTER_PATTERN
        preface_keywords = patterns.PREFACE_KEYWORDS
    else:
        patterns = ChinesePatterns()
        chapter_pattern = patterns.CHAPTER_PATTERN
        preface_keywords = patterns.PREFACE_KEYWORDS

    # Optimized: Use finditer() instead of split()
    all_matches = list(chapter_pattern.finditer(content))

    # Validate matches to filter out inline references (if enabled)
    if config.enable_chapter_validation:
        chapter_matches = [match for match in all_matches if is_valid_chapter_title(match, content, language)]
        if len(all_matches) != len(chapter_matches):
            logger.info(f"Filtered out {len(all_matches) - len(chapter_matches)} inline chapter references")
    else:
        chapter_matches = all_matches

    chapter_list = []

    # If no chapter titles found, return empty list (let parent function handle)
    if not chapter_matches:
        return chapter_list

    # Process first part (possibly preface content without chapter title)
    first_chapter_start = chapter_matches[0].start()
    if first_chapter_start > 0 and content[:first_chapter_start].strip():
        preface_content = content[:first_chapter_start].strip()
        sections = parse_sections_from_content(preface_content, language)
        preface_title = "前言" if language == 'chinese' else "Preface"
        if sections:
            chapter_list.append(Chapter(title=preface_title, content="", sections=sections))
        else:
            chapter_list.append(Chapter(title=preface_title, content=preface_content, sections=[]))

    # Process each matched chapter
    seen_titles = set()  # Track seen chapter titles

    for i, match in enumerate(chapter_matches):
        chapter_title = match.group(1).strip()

        # Get chapter content (from end of current match to start of next match, or end of text)
        chapter_start = match.end()
        chapter_end = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(content)
        chapter_content = content[chapter_start:chapter_end].strip('\n\r')

        if chapter_title and chapter_title not in seen_titles:  # Ensure title is not empty and not duplicate
            seen_titles.add(chapter_title)
            # Further analyze chapter content for sections
            sections = parse_sections_from_content(chapter_content, language)
            if sections:
                # If has sections, chapter content is empty (all content is in sections)
                chapter_list.append(Chapter(title=chapter_title, content="", sections=sections))
            else:
                # If no sections, chapter directly contains content
                if not chapter_content.strip():
                    empty_content = "此章节内容为空。" if language == 'chinese' else "This chapter is empty."
                    chapter_content = empty_content
                chapter_list.append(Chapter(title=chapter_title, content=chapter_content, sections=[]))

    return chapter_list


def parse_sections_from_content(content: str, language: str = 'chinese') -> List[Section]:
    """
    Split sections from given chapter content.
    Supports both Chinese and English section formats.
    Optimized version using finditer() for better performance.

    :param content: Chapter content
    :param language: Language type, 'chinese' or 'english'
    :return: Section list, each section contains title and content
    """
    if not content or not content.strip():
        return []

    # Select corresponding patterns based on language
    if language == 'english':
        patterns = EnglishPatterns()
        # Try multiple section patterns for English
        section_patterns = [patterns.SECTION_PATTERN, patterns.NUMBERED_SECTION_PATTERN]
    else:
        patterns = ChinesePatterns()
        section_patterns = [patterns.SECTION_PATTERN]

    section_list = []
    section_matches = None
    active_pattern = None

    # Try different section patterns
    for pattern in section_patterns:
        matches = list(pattern.finditer(content))
        if matches:  # Found matching pattern
            section_matches = matches
            active_pattern = pattern
            break

    # If no section pattern found, return empty list
    if not section_matches:
        return section_list

    # Handle first part (chapter preface, content without section title)
    first_section_start = section_matches[0].start()
    if first_section_start > 0 and content[:first_section_start].strip():
        preface_title = "章节序言" if language == 'chinese' else "Chapter Preface"
        section_list.append(Section(title=preface_title, content=content[:first_section_start].strip()))

    # Process each matched section
    seen_titles = set()  # Track seen section titles
    for i, match in enumerate(section_matches):
        section_title = match.group(1).strip()

        # Get section content (from end of current match to start of next match, or end of text)
        section_start = match.end()
        section_end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(content)
        section_content = content[section_start:section_end].strip('\n\r')

        if section_title and section_title not in seen_titles:  # Ensure title is not empty and not duplicate
            seen_titles.add(section_title)
            # Ensure section content is not empty
            if not section_content.strip():
                empty_content = "此节内容为空。" if language == 'chinese' else "This section is empty."
                section_content = empty_content
            section_list.append(Section(title=section_title, content=section_content))

    return section_list


def validate_and_merge_chapters(chapters: List[Chapter], language: str = 'chinese', min_length: int = 500) -> List[Chapter]:
    """
    Validate chapter structure and merge chapters that are too short (likely misidentified).

    :param chapters: List of chapters to validate
    :param language: Language type, 'chinese' or 'english'
    :param min_length: Minimum chapter length in characters
    :return: Validated and merged chapter list
    """
    if not chapters:
        return chapters

    valid_chapters = []
    accumulated_content = ""
    accumulated_title = None

    for i, chapter in enumerate(chapters):
        # Calculate total content length (chapter content + all sections)
        total_content = chapter.content
        for section in chapter.sections:
            total_content += section.content

        content_length = len(total_content.strip())

        # Check if chapter is too short
        if content_length < min_length:
            logger.warning(f"Chapter '{chapter.title}' is too short ({content_length} chars), may be misidentified")

            # First chapter or no previous accumulated content
            if not valid_chapters and not accumulated_content:
                # Store this chapter for potential merging
                accumulated_title = chapter.title
                accumulated_content = f"{chapter.title}\n\n{chapter.content}"
            else:
                # Merge into previous chapter or accumulated content
                if valid_chapters:
                    # Merge into last valid chapter
                    last_chapter = valid_chapters[-1]
                    merged_content = last_chapter.content
                    if merged_content:
                        merged_content += f"\n\n{chapter.title}\n{chapter.content}"
                    else:
                        merged_content = f"{chapter.title}\n{chapter.content}"

                    # Keep the original chapter structure but update content
                    valid_chapters[-1] = Chapter(
                        title=last_chapter.title,
                        content=merged_content,
                        sections=last_chapter.sections
                    )
                    logger.info(f"Merged short chapter '{chapter.title}' into '{last_chapter.title}'")
                else:
                    # Add to accumulated content
                    accumulated_content += f"\n\n{chapter.title}\n{chapter.content}"
        else:
            # Chapter is long enough, it's valid
            if accumulated_content:
                # First, add the accumulated content as a chapter
                preface_title = accumulated_title or ("前言" if language == 'chinese' else "Preface")
                valid_chapters.append(Chapter(
                    title=preface_title,
                    content=accumulated_content.strip(),
                    sections=[]
                ))
                accumulated_content = ""
                accumulated_title = None

            # Then add current chapter
            valid_chapters.append(chapter)

    # Handle any remaining accumulated content
    if accumulated_content:
        preface_title = accumulated_title or ("前言" if language == 'chinese' else "Preface")
        valid_chapters.append(Chapter(
            title=preface_title,
            content=accumulated_content.strip(),
            sections=[]
        ))

    logger.info(f"Chapter validation complete: {len(chapters)} -> {len(valid_chapters)} chapters")
    return valid_chapters
