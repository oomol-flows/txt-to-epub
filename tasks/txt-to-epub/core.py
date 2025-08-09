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
        # 检查文件是否存在
        if not os.path.exists(txt_file):
            raise FileNotFoundError(f"文件不存在: {txt_file}")
        
        # 检查文件大小
        file_size = os.path.getsize(txt_file)
        if file_size == 0:
            logger.warning(f"文件为空: {txt_file}")
            return "此文档内容为空。"
        
        # 检测文件编码
        with open(txt_file, 'rb') as f:
            # 读取足够的数据进行编码检测，但不超过1MB
            sample_size = min(file_size, 1024 * 1024)
            raw_data = f.read(sample_size)
            result = chardet.detect(raw_data)
            encoding = result.get('encoding') or 'gb18030'
            confidence = result.get('confidence', 0)
            
            logger.info(f"检测到文件编码: {encoding} (置信度: {confidence:.2f})")

        # 统一使用GB18030编码处理中文编码问题
        if encoding and encoding.lower() in ['gb2312', 'gbk']:
            encoding = 'gb18030'
        
        # 尝试多种编码读取文件
        encodings_to_try = [encoding, 'utf-8', 'gb18030', 'gbk', 'utf-16', 'latin1']
        
        for enc in encodings_to_try:
            if not enc:
                continue
            try:
                with open(txt_file, 'r', encoding=enc, errors='replace') as f:
                    content = f.read()
                    # 验证内容是否合理（不全是替换字符）
                    if content and content.count('�') / len(content) < 0.1:  # 替换字符少于10%
                        logger.info(f"成功使用编码 {enc} 读取文件")
                        return content
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # 如果所有编码都失败，使用最后的备用方案
        logger.warning(f"所有编码尝试失败，使用备用方案读取文件: {txt_file}")
        with open(txt_file, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
            
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
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
    # 验证输入参数
    if not txt_file or not txt_file.strip():
        raise ValueError("输入文件路径不能为空")
    
    if not epub_file or not epub_file.strip():
        raise ValueError("输出文件路径不能为空")
    
    if not txt_file.lower().endswith('.txt'):
        raise ValueError("输入文件必须是.txt格式")
    
    if not epub_file.lower().endswith('.epub'):
        raise ValueError("输出文件必须是.epub格式")

    logger.info(f"开始转换: {txt_file} -> {epub_file}")
    
    try:
        # 创建EPUB书籍
        book = _create_epub_book(title, author, cover_image)
        
        # 读取并分析文本内容
        content = _read_txt_file(txt_file)
        
        # 验证内容不为空
        if not content or not content.strip():
            logger.warning("文件内容为空，创建默认内容")
            content = "此文档内容为空或无法解析。"
        
        logger.info(f"文件内容长度: {len(content)} 字符")
        
        volumes = parse_hierarchical_content(content)
        
        # 验证解析结果
        if not volumes:
            logger.error("解析失败，没有生成任何卷")
            raise Exception("文档解析失败，无法生成EPUB")
        
        logger.info(f"解析完成，共生成 {len(volumes)} 个卷")

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
        
        logger.info(f"EPUB转换完成: {epub_file}")
        
    except Exception as e:
        logger.error(f"转换过程中发生错误: {e}")
        raise Exception(f"EPUB转换失败: {e}")
