import os
import logging
import chardet
from typing import Optional
from ebooklib import epub

from .data_structures import Volume
from .parser import parse_hierarchical_content
from .css import add_css_style
from .html_generator import create_volume_page, create_chapter_page, create_section_page, create_chapter

# 配置日志
logger = logging.getLogger(__name__)


def _create_epub_book(title: str, author: str, cover_image: Optional[str] = None) -> epub.EpubBook:
    """创建一个新的EPUB书籍并设置元数据。"""
    book = epub.EpubBook()
    book.set_title(title)
    book.set_language('zh')  # 设置语言为中文
    book.add_author(author)

    if cover_image:
        _set_cover_image(book, cover_image)

    return book


def _set_cover_image(book: epub.EpubBook, cover_image: str) -> None:
    """设置书籍的封面图片。"""
    try:
        with open(cover_image, 'rb') as cover_file:
            book.set_cover('cover.png', cover_file.read())
    except IOError as e:
        logger.error(f"无法读取封面图片 {cover_image}: {e}")


def _read_txt_file(txt_file: str) -> str:
    """读取文本文件内容，自动检测文件编码。"""
    try:
        # 检测文件编码
        with open(txt_file, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result.get('encoding') or 'gb18030'

        # 统一使用GB18030编码处理中文编码问题
        if encoding.lower() in ['gb2312', 'gbk']:
            encoding = 'gb18030'

        # 读取文件内容，使用错误替换策略
        with open(txt_file, 'r', encoding=encoding, errors='replace') as f:
            return f.read()
            
    except IOError as e:
        raise IOError(f"无法读取文件 {txt_file}: {e}")
    except Exception as e:
        raise Exception(f"读取文件时发生错误 {txt_file}: {e}")


def _write_epub_file(epub_file: str, book: epub.EpubBook) -> None:
    """写入EPUB文件。"""
    try:
        epub.write_epub(epub_file, book, {})
        logger.info(f"成功生成EPUB文件: {epub_file}")
    except Exception as e:
        raise Exception(f"无法写入EPUB文件 {epub_file}: {e}")


def txt_to_epub(txt_file: str, epub_file: str, title: str = '我的书', 
                author: str = '未知', cover_image: Optional[str] = None) -> None:
    """
    将文本文件转换为EPUB格式的电子书, 支持中文内容。

    :param txt_file: 输入的文本文件路径
    :param epub_file: 输出的EPUB文件路径
    :param title: 书籍标题
    :param author: 作者名称
    :param cover_image: 封面图片路径（可选）
    """
    if not txt_file.endswith('.txt'):
        raise ValueError("输入文件必须是.txt格式")

    # 创建EPUB书籍
    book = _create_epub_book(title, author, cover_image)
    
    # 读取并分析文本内容
    content = _read_txt_file(txt_file)
    volumes = parse_hierarchical_content(content)

    # 添加卷、章节和节到书籍
    chapter_items = []
    toc_structure = []
    chapter_counter = 1
    volume_counter = 1
    
    for volume in volumes:
        if volume.title:  # 如果有卷标题
            # 为卷创建一个页面
            volume_file_name = f"volume_{volume_counter}.xhtml"
            volume_page = create_volume_page(volume.title, volume_file_name, len(volume.chapters))
            book.add_item(volume_page)
            chapter_items.append(volume_page)
            
            # 创建卷的目录链接（顶级，不缩进）
            volume_link = epub.Link(volume_file_name, volume.title, f"volume_{volume_counter}")
            volume_chapters = []
            
            for chapter in volume.chapters:
                if chapter.sections:  # 章节有小节
                    # 创建章节页面
                    chapter_file_name = f"chap_{chapter_counter}.xhtml"
                    chapter_page = create_chapter_page(chapter.title, chapter.content, chapter_file_name, len(chapter.sections))
                    book.add_item(chapter_page)
                    chapter_items.append(chapter_page)
                    
                    # 创建章节的目录链接（相对卷缩进一级）
                    chapter_link = epub.Link(chapter_file_name, chapter.title, f"chap_{chapter_counter}")
                    section_links = []
                    section_counter = 1
                    
                    # 处理章节下的小节
                    for section in chapter.sections:
                        section_file_name = f"chap_{chapter_counter}_sec_{section_counter}.xhtml"
                        section_page = create_section_page(section.title, section.content, section_file_name)
                        book.add_item(section_page)
                        chapter_items.append(section_page)
                        # 创建节的目录链接（相对章再缩进一级）
                        section_links.append(epub.Link(section_file_name, section.title, f"chap_{chapter_counter}_sec_{section_counter}"))
                        section_counter += 1
                    
                    # 将章节和其小节作为嵌套结构添加
                    volume_chapters.append((chapter_link, section_links))
                else:  # 章节没有小节，直接添加章节内容
                    chapter_page = create_chapter(chapter.title, chapter.content, f"chap_{chapter_counter}.xhtml")
                    book.add_item(chapter_page)
                    chapter_items.append(chapter_page)
                    # 章节直接作为卷的子项（相对卷缩进一级）
                    volume_chapters.append(epub.Link(f"chap_{chapter_counter}.xhtml", chapter.title, f"chap_{chapter_counter}"))
                
                chapter_counter += 1
            
            # 添加卷到目录结构：卷标题 + 其下的章节和节的层次结构
            toc_structure.append((volume_link, volume_chapters))
            volume_counter += 1
        else:  # 没有卷，直接添加章节
            for chapter in volume.chapters:
                if chapter.sections:  # 章节有小节
                    # 创建章节页面
                    chapter_file_name = f"chap_{chapter_counter}.xhtml"
                    chapter_page = create_chapter_page(chapter.title, chapter.content, chapter_file_name, len(chapter.sections))
                    book.add_item(chapter_page)
                    chapter_items.append(chapter_page)
                    
                    # 创建章节的目录链接（顶级）
                    chapter_link = epub.Link(chapter_file_name, chapter.title, f"chap_{chapter_counter}")
                    section_links = []
                    section_counter = 1
                    
                    # 处理章节下的小节
                    for section in chapter.sections:
                        section_file_name = f"chap_{chapter_counter}_sec_{section_counter}.xhtml"
                        section_page = create_section_page(section.title, section.content, section_file_name)
                        book.add_item(section_page)
                        chapter_items.append(section_page)
                        # 创建节的目录链接（相对章缩进一级）
                        section_links.append(epub.Link(section_file_name, section.title, f"chap_{chapter_counter}_sec_{section_counter}"))
                        section_counter += 1
                    
                    # 将章节和其小节作为嵌套结构添加
                    toc_structure.append((chapter_link, section_links))
                else:  # 章节没有小节，直接添加章节内容
                    chapter_page = create_chapter(chapter.title, chapter.content, f"chap_{chapter_counter}.xhtml")
                    book.add_item(chapter_page)
                    chapter_items.append(chapter_page)
                    # 章节作为顶级项
                    toc_structure.append(epub.Link(f"chap_{chapter_counter}.xhtml", chapter.title, f"chap_{chapter_counter}"))
                
                chapter_counter += 1

    # 设置书籍结构
    book.toc = toc_structure
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # 添加样式和设置spine
    add_css_style(book)
    book.spine = ['nav'] + chapter_items

    # 确保输出目录存在并写入文件
    os.makedirs(os.path.dirname(epub_file), exist_ok=True)
    _write_epub_file(epub_file, book)
