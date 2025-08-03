import os
import re
import logging
from typing import Dict, Optional, List, Tuple, Union, NamedTuple
import chardet
from oocana import Context
from ebooklib import epub

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义数据结构
class Section(NamedTuple):
    """表示一个节的数据结构"""
    title: str
    content: str

class Chapter(NamedTuple):
    """表示一个章的数据结构"""
    title: str
    content: str
    sections: List[Section]

class Volume(NamedTuple):
    """表示一个卷/部/篇的数据结构"""
    title: Optional[str]
    chapters: List[Chapter]

def main(params: Dict[str, Optional[str]], context: Context) -> Dict[str, str]:
    """
    主函数，负责将文本文件转换为EPUB格式的电子书。

    :param params: 包含输入参数的字典
    :param context: 上下文对象
    :return: 包含输出文件路径的字典
    """
    # 提取必需参数
    required_params = ['txt_file', 'book_title', 'author', 'epub_dir', 'cover_image']
    
    # 校验所有必需参数都不为空
    if all(params.get(param) for param in required_params):
        epub_file = os.path.join(params['epub_dir'], f"{params['book_title']}.epub")
        txt_to_epub(
            txt_file=params['txt_file'],
            epub_file=epub_file,
            title=params['book_title'],
            author=params['author'],
            cover_image=params['cover_image']
        )
        return {"epub_file": epub_file}
    
    logger.warning("缺少必需参数，无法生成EPUB文件")
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


def create_epub_book(title: str, author: str, cover_image: Optional[str] = None) -> epub.EpubBook:
    """
    创建一个新的EPUB书籍并设置元数据。

    :param title: 书籍标题
    :param author: 作者名称
    :param cover_image: 封面图片路径（可选）
    :return: EpubBook对象
    """
    book = epub.EpubBook()
    book.set_title(title)
    book.set_language('zh')  # 设置语言为中文
    book.add_author(author)

    if cover_image:
        set_cover_image(book, cover_image)

    return book

def set_cover_image(book: epub.EpubBook, cover_image: str) -> None:
    """
    设置书籍的封面图片。

    :param book: EpubBook对象
    :param cover_image: 封面图片路径
    """
    try:
        with open(cover_image, 'rb') as cover_file:
            book.set_cover('cover.png', cover_file.read())
    except IOError as e:
        raise IOError(f"无法读取封面图片 {cover_image}: {e}")

def read_txt_file(txt_file: str) -> str:
    """
    读取文本文件内容，自动检测文件编码。

    :param txt_file: 文本文件路径
    :return: 文件内容
    """
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


def parse_hierarchical_content(content: str) -> List[Volume]:
    """
    将文本内容分割成卷、章、节的三级层次结构。
    支持"卷"、"部"、"篇"作为同一层级的单位。

    :param content: 文本内容
    :return: 卷列表，包含完整的层次结构
    """
    # 匹配卷/部/篇标题模式（支持数字和中文数字，包括大写中文数字）
    volume_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})[卷部篇]\s*[^\n]*)')
    # 匹配章节标题模式（支持数字和中文数字，包括大写中文数字）
    chapter_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s*[^\n]*)')
    # 匹配节标题模式（支持数字和中文数字，包括大写中文数字）
    section_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})节\s*[^\n]*)')
    
    # 首先按卷分割
    volume_parts = volume_pattern.split(content)
    
    volumes = []
    
    if len(volume_parts) == 1:
        # 没有卷，只有章节
        chapters = parse_chapters_from_content(volume_parts[0])
        if chapters:
            volumes.append(Volume(title=None, chapters=chapters))
    else:
        # 处理第一部分（可能是序言等，没有卷标题的内容）
        if volume_parts[0].strip():
            pre_chapters = parse_chapters_from_content(volume_parts[0])
            if pre_chapters:
                volumes.append(Volume(title=None, chapters=pre_chapters))
        
        # 处理有卷标题的部分，步长为3（因为split会产生分组）
        for i in range(1, len(volume_parts), 3):
            if i + 2 < len(volume_parts):
                volume_title = volume_parts[i].strip()
                volume_content = volume_parts[i + 2]
                chapters = parse_chapters_from_content(volume_content)
                if chapters:
                    volumes.append(Volume(title=volume_title, chapters=chapters))

    return volumes


def parse_chapters_from_content(content: str) -> List[Chapter]:
    """
    从给定的内容中分割出章节和节。

    :param content: 文本内容
    :return: 章节列表，每个章节包含标题、内容和节列表
    """
    # 匹配章节标题模式（支持数字和中文数字，包括大写中文数字）
    chapter_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s*[^\n]*)')
    chapters_raw = chapter_pattern.split(content)

    chapter_list = []
    # split结果包含分组，所以步长为3
    for i in range(1, len(chapters_raw), 3):
        if i + 2 < len(chapters_raw):
            chapter_title = chapters_raw[i].strip()
            chapter_content = chapters_raw[i + 2].strip('\n\r')
            if chapter_title:  # 确保章节标题不为空
                # 进一步分析章节内容，看是否包含节
                sections = parse_sections_from_content(chapter_content)
                if sections:
                    # 如果有节，章节内容为空（内容都在节中）
                    chapter_list.append(Chapter(title=chapter_title, content="", sections=sections))
                else:
                    # 如果没有节，章节直接包含内容
                    chapter_list.append(Chapter(title=chapter_title, content=chapter_content, sections=[]))

    return chapter_list


def parse_sections_from_content(content: str) -> List[Section]:
    """
    从给定的章节内容中分割出节。

    :param content: 章节内容
    :return: 节列表，每个节包含标题和内容
    """
    # 匹配节标题模式（支持数字和中文数字，包括大写中文数字）
    section_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})节\s*[^\n]*)')
    sections_raw = section_pattern.split(content)

    section_list = []
    if len(sections_raw) == 1:
        # 没有节标题，返回空列表
        return section_list
    
    # 处理第一部分（章节序言，没有节标题的内容）
    if sections_raw[0].strip():
        section_list.append(Section(title="", content=sections_raw[0].strip()))
    
    # split结果包含分组，所以步长为3
    for i in range(1, len(sections_raw), 3):
        if i + 2 < len(sections_raw):
            section_title = sections_raw[i].strip()
            section_content = sections_raw[i + 2].strip('\n\r')
            if section_title:  # 确保节标题不为空
                section_list.append(Section(title=section_title, content=section_content))

    return section_list


def split_into_volumes_and_chapters(content: str) -> List[Tuple[Optional[str], List[Tuple[str, str]]]]:
    """
    将文本内容分割成卷和章节，支持层级结构。
    此函数保留用于向后兼容。

    :param content: 文本内容
    :return: 卷列表，每个卷包含卷标题（可为None）和章节列表
    """
    volumes = parse_hierarchical_content(content)
    result = []
    
    for volume in volumes:
        chapters = []
        for chapter in volume.chapters:
            if chapter.sections:
                # 如果有节，将所有节的内容合并到章节中
                combined_content = chapter.content
                for section in chapter.sections:
                    if section.title:
                        combined_content += f"\n\n{section.title}\n{section.content}"
                    else:
                        combined_content += f"\n{section.content}"
                chapters.append((chapter.title, combined_content))
            else:
                chapters.append((chapter.title, chapter.content))
        result.append((volume.title, chapters))
    
    return result


def split_chapters_from_content(content: str) -> List[Tuple[str, str]]:
    """
    从给定的内容中分割出章节。
    此函数保留用于向后兼容。

    :param content: 文本内容
    :return: 章节列表，每个章节包含标题和内容
    """
    chapters = parse_chapters_from_content(content)
    result = []
    
    for chapter in chapters:
        if chapter.sections:
            # 如果有节，将所有节的内容合并到章节中
            combined_content = chapter.content
            for section in chapter.sections:
                if section.title:
                    combined_content += f"\n\n{section.title}\n{section.content}"
                else:
                    combined_content += f"\n{section.content}"
            result.append((chapter.title, combined_content))
        else:
            result.append((chapter.title, chapter.content))
    
    return result


def split_into_chapters(content: str) -> List[Tuple[str, str]]:
    """
    将文本内容分割成多个章节，保留章节标题。
    此函数保留用于向后兼容。

    :param content: 文本内容
    :return: 章节列表，每个章节包含标题和内容
    """
    volumes = split_into_volumes_and_chapters(content)
    all_chapters = []
    for _, chapters in volumes:
        all_chapters.extend(chapters)
    return all_chapters

def add_css_style(book: epub.EpubBook) -> None:
    """添加现代化CSS样式到EPUB书籍。"""
    style = """
    /* 现代化电子书样式 */
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    
    body {
        font-family: "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun", serif;
        font-size: 1.1em;
        line-height: 1.8;
        color: #2c3e50;
        background: #fefefe;
        max-width: 100%;
        margin: 0 auto;
        padding: 2rem 1.5rem;
    }
    
    /* 标题样式 */
    h1 {
        font-size: 1.5em;
        font-weight: 600;
        text-align: center;
        color: #1a1a1a;
        margin: 1.5rem 0 2rem 0;
        padding: 1rem 0;
    }
    
    h2 {
        font-size: 1.3em;
        color: #34495e;
        margin: 1.5rem 0 1rem 0;
        font-weight: 500;
    }
    
    /* 段落样式 */
    p {
        text-indent: 2em;
        margin-bottom: 1.2rem;
        text-align: justify;
        word-wrap: break-word;
    }
    
    /* 预格式化文本样式 */
    pre {
        font-family: "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
        font-size: 1em;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 1rem 0;
        padding: 0;
        background: transparent;
        border: none;
    }
    
    /* 响应式设计 */
    @media screen and (max-width: 768px) {
        body {
            padding: 1rem;
            font-size: 1em;
        }
        
        h1 {
            font-size: 1.3em;
            margin: 1rem 0 1.5rem 0;
        }
        
        h2 {
            font-size: 1.2em;
        }
    }
    
    /* 优化中文排版 */
    .chinese-text {
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    """
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style.encode('utf-8')
    )
    book.add_item(nav_css)

def write_epub_file(epub_file: str, book: epub.EpubBook) -> None:
    """写入EPUB文件。"""
    try:
        epub.write_epub(epub_file, book, {})
        logger.info(f"成功生成EPUB文件: {epub_file}")
    except Exception as e:
        raise Exception(f"无法写入EPUB文件 {epub_file}: {e}")

def create_chapter(title: str, content: str, file_name: str) -> epub.EpubHtml:
    """创建EPUB章节。"""
    chapter = epub.EpubHtml(title=title, file_name=file_name, lang='zh')
    
    if content:
        # 使用<pre>标签保留原始格式
        chapter.content = f'<h1>{title}</h1><pre>{content}</pre>'
    else:
        chapter.content = f'<h1>{title}</h1>'
    
    return chapter


def create_volume_page(volume_title: str, file_name: str, chapter_count: int) -> epub.EpubHtml:
    """
    创建卷/部/篇的页面，使用现代化设计。
    
    :param volume_title: 卷标题
    :param file_name: 文件名
    :param chapter_count: 章节数量
    :return: EpubHtml对象
    """
    volume_page = epub.EpubHtml(title=volume_title, file_name=file_name, lang='zh')
    
    # 确定单位名称和装饰图标
    if "卷" in volume_title:
        unit_name = "卷"
        icon = "📖"
    elif "部" in volume_title:
        unit_name = "部"
        icon = "📚"
    elif "篇" in volume_title:
        unit_name = "篇"
        icon = "📜"
    else:
        unit_name = "卷"
        icon = "📖"
    
    # 创建简洁的卷页面内容
    volume_page.content = f'''
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{volume_title}</title>
        <link rel="stylesheet" type="text/css" href="style/nav.css"/>
    </head>
    <body class="chinese-text">
        <h1>{volume_title}</h1>
        <div style="margin-top: 2rem; text-align: center;">
            <p style="color: #7f8c8d; font-size: 0.9em;">
                本{unit_name}包含 {chapter_count} 章内容
            </p>
        </div>
    </body>
    </html>
    '''
    
    return volume_page


def create_chapter_page(chapter_title: str, chapter_content: str, file_name: str, section_count: int) -> epub.EpubHtml:
    """
    创建章节页面（用于有小节的章节），使用现代化设计。
    
    :param chapter_title: 章节标题
    :param chapter_content: 章节内容（通常为空，因为内容在小节中）
    :param file_name: 文件名
    :param section_count: 小节数量
    :return: EpubHtml对象
    """
    chapter_page = epub.EpubHtml(title=chapter_title, file_name=file_name, lang='zh')
    
    # 创建优雅的章节页面内容
    if chapter_content.strip():
        chapter_page.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{chapter_title}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <h1>{chapter_title}</h1>
            <div style="margin-top: 1.5rem;">
                <pre>{chapter_content}</pre>
            </div>
            
            <div style="margin-top: 3rem; text-align: center;">
                <p style="color: #7f8c8d; font-size: 0.9em;">
                    本章包含 {section_count} 个小节
                </p>
            </div>
        </body>
        </html>
        '''
    else:
        chapter_page.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{chapter_title}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <h1>{chapter_title}</h1>
            <div style="margin-top: 2rem; text-align: center;">
                <p style="color: #7f8c8d; font-size: 0.9em;">
                    本章共分为 {section_count} 个小节
                </p>
            </div>
        </body>
        </html>
        '''
    
    return chapter_page


def create_section_page(section_title: str, section_content: str, file_name: str) -> epub.EpubHtml:
    """
    创建节页面，使用现代化设计。
    
    :param section_title: 节标题
    :param section_content: 节内容
    :param file_name: 文件名
    :return: EpubHtml对象
    """
    section_page = epub.EpubHtml(title=section_title, file_name=file_name, lang='zh')
    
    if section_title:
        section_page.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{section_title}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <h2>{section_title}</h2>
            <div style="margin-top: 1rem;">
                <pre>{section_content}</pre>
            </div>
        </body>
        </html>
        '''
    else:
        # 无标题的节（章节序言）
        section_page.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>章节序言</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <div style="margin-top: 1rem;">
                <pre>{section_content}</pre>
            </div>
        </body>
        </html>
        '''
    
    return section_page


def create_chapter(title: str, content: str, file_name: str) -> epub.EpubHtml:
    """创建EPUB章节，使用现代化设计。"""
    chapter = epub.EpubHtml(title=title, file_name=file_name, lang='zh')
    
    if content:
        chapter.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <h1>{title}</h1>
            <div style="margin-top: 1.5rem;">
                <pre>{content}</pre>
            </div>
        </body>
        </html>
        '''
    else:
        chapter.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <h1>{title}</h1>
        </body>
        </html>
        '''
    
    return chapter
