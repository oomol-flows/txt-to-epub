import os
import logging
from typing import Dict, Optional
from oocana import Context
from ebooklib import epub

from .data_structures import Volume
from .parser import parse_hierarchical_content
from .utils import create_epub_book, read_txt_file, write_epub_file
from .css import add_css_style
from .html_generator import create_volume_page, create_chapter_page, create_section_page, create_chapter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(params: Dict[str, Optional[str]], context: Context) -> Dict[str, str]:
    """
    主函数，负责将文本文件转换为EPUB格式的电子书。

    :param params: 包含输入参数的字典
    :param context: 上下文对象
    :return: 包含输出文件路径的字典
    """
    # 只有 txt_file 和 epub_dir 为必填参数
    required_params = ['txt_file', 'epub_dir']
    
    # 校验必需参数都不为空
    if all(params.get(param) for param in required_params):
        # 获取必需参数
        txt_file = params['txt_file']
        epub_dir = params['epub_dir']
        
        # 确保参数不为None
        if not txt_file or not epub_dir:
            logger.warning("必需参数不能为空")
            return {"epub_file": ""}
        
        # 如果 book_title 未提供，使用不含后缀的文件名
        book_title = params.get('book_title')
        if not book_title:
            txt_filename = os.path.basename(txt_file)
            book_title = os.path.splitext(txt_filename)[0]
        
        # 设置默认值
        author = params.get('author') or '未知'
        cover_image = params.get('cover_image')  # 可为None
        
        epub_file = os.path.join(epub_dir, f"{book_title}.epub")
        txt_to_epub(
            txt_file=txt_file,
            epub_file=epub_file,
            title=book_title,
            author=author,
            cover_image=cover_image
        )
        return {"epub_file": epub_file}
    
    logger.warning("缺少必需参数（txt_file 和 epub_dir），无法生成EPUB文件")
    return {"epub_file": ""}


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
    book = create_epub_book(title, author, cover_image)
    
    # 读取并分析文本内容
    content = read_txt_file(txt_file)
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
    write_epub_file(epub_file, book)
