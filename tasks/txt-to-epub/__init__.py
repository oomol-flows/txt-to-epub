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
    # 只有 txt_file 和 epub_dir 为必填参数
    required_params = ['txt_file', 'epub_dir']
    
    # 校验必需参数都不为空
    if all(params.get(param) for param in required_params):
        # 如果 book_title 未提供，使用不含后缀的文件名
        book_title = params.get('book_title')
        if not book_title:
            txt_filename = os.path.basename(params['txt_file'])
            book_title = os.path.splitext(txt_filename)[0]
        
        # 设置默认值
        author = params.get('author') or '未知'
        cover_image = params.get('cover_image')  # 可为None
        
        epub_file = os.path.join(params['epub_dir'], f"{book_title}.epub")
        txt_to_epub(
            txt_file=params['txt_file'],
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
    volume_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})[卷部篇]\s+[^\n]*)')
    # 匹配章节标题模式（支持数字和中文数字，包括大写中文数字）
    chapter_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s+[^\n]*)')
    # 匹配节标题模式（支持数字和中文数字，包括大写中文数字）
    section_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})节\s+[^\n]*)')
    
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
    chapter_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s+[^\n]*)')
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
    section_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})节\s+[^\n]*)')
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
    """添加精美的多看风格CSS样式到EPUB书籍。"""
    style = """
    /* =====================================
       精美EPUB样式 - 基于多看模板优化设计
       ===================================== */
    
    /* 基础重置与字体设置 */
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    
    body {
        /* 多级字体回退，确保最佳显示效果 */
        font-family: "DK-SONGTI", "方正宋三简体", "方正书宋", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "SimSun", "宋体", serif;
        font-size: 16px;
        line-height: 1.8;
        color: #2c2c2c;
        background: #fefefe;
        max-width: 100%;
        margin: 0 auto;
        padding: 2rem 1.5rem;
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* =====================================
       卷/部/篇标题样式 (最高级别)
       ===================================== */
    .volume-title {
        font-family: "DK-XIAOBIAOSONG", "方正小标宋简体", "STZhongsong", "华文中宋", serif;
        font-size: 2.4em;
        font-weight: normal;
        text-align: center;
        color: #91531d;
        margin: 3rem 0 4rem 0;
        padding: 2rem 0;
        border-bottom: 4px solid #e8c696;
        text-shadow: 1px 1px 3px rgba(145, 83, 29, 0.2);
        position: relative;
    }
    
    .volume-title::before {
        content: "";
        position: absolute;
        top: -0.5rem;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        height: 2px;
        background: linear-gradient(to right, transparent, #91531d, transparent);
    }
    
    /* =====================================
       章标题样式 (中级别)
       ===================================== */
    .chapter-title {
        font-family: "DK-XIAOBIAOSONG", "方正小标宋简体", "STZhongsong", "华文中宋", serif;
        font-size: 2em;
        font-weight: normal;
        text-align: center;
        color: #1f4a92;
        margin: 2.5rem 0 3rem 0;
        padding: 1.5rem 0;
        border-bottom: 2px solid #1f4a92;
        position: relative;
    }
    
    .chapter-title::after {
        content: "◊";
        position: absolute;
        bottom: -0.8rem;
        left: 50%;
        transform: translateX(-50%);
        color: #1f4a92;
        font-size: 0.8em;
        background: #fefefe;
        padding: 0 0.5rem;
    }
    
    /* =====================================
       节标题样式 (低级别)
       ===================================== */
    .section-title {
        font-family: "DK-HEITI", "方正兰亭黑简体", "SimHei", "黑体", sans-serif;
        font-size: 1.4em;
        font-weight: normal;
        color: #478686;
        margin: 2rem 0 1.5rem 0;
        padding: 0.8rem 0 0.8rem 1.2rem;
        border-left: 5px solid #478686;
        background: linear-gradient(to right, rgba(71, 134, 134, 0.05), transparent);
        position: relative;
    }
    
    .section-title::before {
        content: "▸";
        position: absolute;
        left: -0.2rem;
        color: #478686;
        font-size: 0.8em;
    }
    
    /* =====================================
       兼容性标题样式
       ===================================== */
    h1 {
        font-family: "DK-XIAOBIAOSONG", "方正小标宋简体", "STZhongsong", "华文中宋", serif;
        font-size: 2em;
        font-weight: normal;
        text-align: center;
        color: #1f4a92;
        margin: 2.5rem 0 3rem 0;
        padding: 1.5rem 0;
        border-bottom: 2px solid #1f4a92;
    }
    
    h2 {
        font-family: "DK-HEITI", "方正兰亭黑简体", "SimHei", "黑体", sans-serif;
        font-size: 1.4em;
        font-weight: normal;
        color: #478686;
        margin: 2rem 0 1.5rem 0;
        padding: 0.8rem 0 0.8rem 1.2rem;
        border-left: 5px solid #478686;
    }
    
    h3 {
        font-family: "DK-HEITI", "方正兰亭黑简体", "SimHei", "黑体", sans-serif;
        font-size: 1.2em;
        font-weight: normal;
        color: #91531d;
        margin: 1.8rem 0 1.2rem 2rem;
    }
    
    /* =====================================
       正文段落样式
       ===================================== */
    p {
        font-family: "DK-SONGTI", "方正宋三简体", "方正书宋", "Noto Serif CJK SC", "SimSun", "宋体", serif;
        font-size: 16px;
        line-height: 1.8;
        text-indent: 2em;
        margin-bottom: 1.2em;
        text-align: justify;
        word-wrap: break-word;
        color: #2c2c2c;
    }
    
    /* 特殊段落样式 */
    p.text0 {
        text-indent: 0em;
    }
    
    p.reference {
        font-family: "DK-KAITI", "方正楷体", "华文楷体", "KaiTi", "楷体", serif;
        font-style: italic;
        color: #555;
        background: rgba(145, 83, 29, 0.03);
        padding: 0.8rem 1.2rem;
        margin: 1.5rem 0;
        border-left: 3px solid #91531d;
        text-indent: 2em;
    }
    
    p.reference-center {
        font-family: "DK-KAITI", "方正楷体", "华文楷体", "KaiTi", "楷体", serif;
        text-align: center;
        font-style: italic;
        color: #666;
        margin: 1.5rem 0;
        text-indent: 0em;
    }
    
    /* =====================================
       预格式化文本样式
       ===================================== */
    pre {
        font-family: "DK-SONGTI", "方正宋三简体", "方正书宋", "Noto Serif CJK SC", "SimSun", "宋体", serif;
        font-size: 16px;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 1.5rem 0;
        padding: 0;
        background: transparent;
        border: none;
        color: #2c2c2c;
    }
    
    /* =====================================
       图片和图注样式
       ===================================== */
    img.duokan-image {
        width: 100%;
        height: auto;
        margin: 1.5rem 0;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .duokan-image-single {
        width: 100%;
        text-align: center;
        margin: 1.5rem 0;
    }
    
    p.duokan-note {
        font-family: "DK-KAITI", "方正楷体", "华文楷体", "KaiTi", "楷体", serif;
        font-size: 14px;
        color: #666;
        text-align: center;
        text-indent: 0em;
        margin: 0.5rem 0 1.5rem 0;
        font-style: italic;
    }
    
    /* =====================================
       强调和装饰样式
       ===================================== */
    .emphasis {
        color: #91531d;
        font-weight: bold;
    }
    
    .kaiti {
        font-family: "DK-KAITI", "方正楷体", "华文楷体", "KaiTi", "楷体", serif;
    }
    
    .heiti {
        font-family: "DK-HEITI", "方正兰亭黑简体", "SimHei", "黑体", sans-serif;
    }
    
    .songti {
        font-family: "DK-SONGTI", "方正宋三简体", "方正书宋", "SimSun", "宋体", serif;
    }
    
    /* =====================================
       分隔线和装饰元素
       ===================================== */
    .separator {
        text-align: center;
        margin: 3rem 0;
        color: #91531d;
        font-size: 1.2em;
    }
    
    .separator::before {
        content: "❋ ❋ ❋";
        color: #91531d;
        opacity: 0.6;
    }
    
    /* =====================================
       响应式设计
       ===================================== */
    @media screen and (max-width: 768px) {
        body {
            padding: 1rem;
            font-size: 15px;
        }
        
        .volume-title {
            font-size: 2em;
            margin: 2rem 0 3rem 0;
            padding: 1.5rem 0;
        }
        
        .chapter-title {
            font-size: 1.7em;
            margin: 2rem 0 2.5rem 0;
            padding: 1.2rem 0;
        }
        
        .section-title {
            font-size: 1.2em;
            margin: 1.5rem 0 1.2rem 0;
            padding: 0.6rem 0 0.6rem 1rem;
        }
        
        h1 {
            font-size: 1.7em;
            margin: 2rem 0 2.5rem 0;
        }
        
        h2 {
            font-size: 1.2em;
            margin: 1.5rem 0 1.2rem 0;
        }
        
        p {
            font-size: 15px;
            line-height: 1.7;
        }
        
        pre {
            font-size: 15px;
            line-height: 1.7;
        }
    }
    
    @media screen and (max-width: 480px) {
        body {
            padding: 0.8rem;
            font-size: 14px;
        }
        
        .volume-title {
            font-size: 1.8em;
        }
        
        .chapter-title {
            font-size: 1.5em;
        }
        
        .section-title {
            font-size: 1.1em;
        }
        
        p, pre {
            font-size: 14px;
            line-height: 1.6;
        }
    }
    
    /* =====================================
       打印样式优化
       ===================================== */
    @media print {
        body {
            background: white;
            color: black;
            padding: 0;
        }
        
        .volume-title, .chapter-title, .section-title {
            page-break-after: avoid;
        }
        
        p {
            orphans: 3;
            widows: 3;
        }
        
        img {
            max-width: 100%;
            page-break-inside: avoid;
        }
    }
    
    /* =====================================
       中文排版优化
       ===================================== */
    .chinese-text {
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        font-variant-east-asian: proportional-width;
        font-feature-settings: "kern" 1;
    }
    
    /* 禁用连字和优化间距 */
    body {
        font-variant-ligatures: none;
        font-kerning: auto;
        text-size-adjust: 100%;
        -webkit-text-size-adjust: 100%;
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
        <h1 class="volume-title">{volume_title}</h1>
        <div style="margin-top: 3rem; text-align: center;">
            <div style="font-size: 3em; margin-bottom: 2rem;">{icon}</div>
            <p style="color: #2c3e50; font-size: 1.3em; font-weight: 500; margin-bottom: 4rem;">
                本{unit_name}包含 {chapter_count} 章内容
            </p>
            <div style="position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%); width: 100%;">
                <p style="color: #95a5a6; font-size: 0.8em; text-align: center;">
                    oomol.com 开源工作组提供格式转换工具，请用户确保版权合规
                </p>
            </div>
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
            <h1 class="chapter-title">{chapter_title}</h1>
            <div style="margin-top: 1.5rem;">
                <pre>{chapter_content}</pre>
            </div>
            
            <div style="margin-top: 3rem; text-align: center;">
                <div style="font-size: 3em; margin-bottom: 2rem;">📚</div>
                <p style="color: #2c3e50; font-size: 1.3em; font-weight: 500; margin-bottom: 4rem;">
                    本章包含 {section_count} 个小节
                </p>
                <div style="position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%); width: 100%;">
                    <p style="color: #95a5a6; font-size: 0.8em; text-align: center;">
                        oomol.com 开源工作组提供格式转换工具，请用户确保版权合规
                    </p>
                </div>
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
            <h1 class="chapter-title">{chapter_title}</h1>
            <div style="margin-top: 3rem; text-align: center;">
                <div style="font-size: 3em; margin-bottom: 2rem;">📚</div>
                <p style="color: #2c3e50; font-size: 1.3em; font-weight: 500; margin-bottom: 4rem;">
                    本章共分为 {section_count} 个小节
                </p>
                <div style="position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%); width: 100%;">
                    <p style="color: #95a5a6; font-size: 0.8em; text-align: center;">
                        oomol.com 开源工作组提供格式转换工具，请用户确保版权合规
                    </p>
                </div>
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
            <h2 class="section-title">{section_title}</h2>
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
            <h1 class="chapter-title">{title}</h1>
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
            <h1 class="chapter-title">{title}</h1>
        </body>
        </html>
        '''
    
    return chapter
