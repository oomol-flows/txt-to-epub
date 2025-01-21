from calendar import c
from oocana import Context
from ebooklib import epub
import os
import logging
from typing import Dict, Optional
import chardet

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
    # 提取参数
    txt_file = params.get('txt_file')
    book_title = params.get('book_title')
    author = params.get('author')
    cover_image = params.get('cover_image')
    epub_dir = params.get('epub_dir')

    # 校验所有参数都不是空
    if txt_file is not None and book_title is not None and author is not None and epub_dir is not None and cover_image is not None:
        # 生成EPUB文件路径
        epub_file = os.path.join(epub_dir, f"{book_title}.epub")
        # 调用转换函数
        txt_to_epub(txt_file, epub_file, title=book_title, author=author, cover_image=cover_image)
        return {"epub_file": epub_file}
    else:
        return {"epub_file": ""}


def txt_to_epub(txt_file: str, epub_file: str, title: str = '我的书', author: str = '未知', cover_image: Optional[str] = None) -> None:
    """
    将文本文件转换为EPUB格式的电子书, 支持中文内容。

    :param txt_file: 输入的文本文件路径
    :param epub_file: 输出的EPUB文件路径
    :param title: 书籍标题
    :param author: 作者名称
    :param cover_image: 封面图片路径（可选）
    """
    # 参数校验
    if not txt_file.endswith('.txt'):
        raise ValueError("输入文件必须是.txt格式")

    # 创建一个新的EPUB书籍
    book = create_epub_book(title, author, cover_image)

    # 读取txt文件内容
    content = read_txt_file(txt_file)

    # 分割文本为多个章节
    chapters = split_into_chapters(content)

    # 创建章节并添加到书籍中
    for i, (chapter_title, chapter_content) in enumerate(chapters):
        chapter = create_chapter(chapter_title, chapter_content, f"chap_{i+1}.xhtml")
        book.add_item(chapter)

    # 定义书籍的目录结构
    book.toc = [epub.Link(f"chap_{i+1}.xhtml", chapter_title, f"chap_{i+1}") for i, (chapter_title, _) in enumerate(chapters)]

    # 添加默认的NCX和Nav文件
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # 添加CSS样式
    add_css_style(book)

    # 添加章节到书籍的spine
    book.spine = ['nav'] + [item for item in book.get_items() if isinstance(item, epub.EpubHtml)]

    # 确保输出目录存在
    os.makedirs(os.path.dirname(epub_file), exist_ok=True)

    # 写入EPUB文件
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
            encoding = result['encoding']

        # 如果检测到的编码是 None，尝试使用默认编码
        if encoding is None:
            encoding = 'gb18030'  # 或者 'utf-8'

        # 如果检测到的编码是 gb2312 或 gbk，尝试使用 GB18030
        if encoding.lower() in ['gb2312', 'gbk']:
            encoding = 'gb18030'

        # 根据检测到的编码读取文件内容，使用 errors='replace' 处理无法解码的字符
        with open(txt_file, 'r', encoding=encoding, errors='replace') as f:
            return f.read()
    except IOError as e:
        raise IOError(f"无法读取文件 {txt_file}: {e}")
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"无法解码文件 {txt_file}: {e}", e.object, e.start, e.end, e.reason)


def split_into_chapters(content: str) -> list:
    """
    将文本内容分割成多个章节，保留章节标题（如 "第1章 引言" 或 "第一章 引言"）。

    :param content: 文本内容
    :return: 章节列表，每个章节包含标题和内容
    """
    import re
    # 使用正则表达式匹配章节标题（如 "第1章 引言" 或 "第一章 引言"）
    chapter_pattern = re.compile(r'(第([一二三四五六七八九十百千万]+|\d{1,3})章\s*[^\n]*)')
    chapters = chapter_pattern.split(content)

    # 将章节标题和内容组合成列表
    chapter_list = []
    for i in range(1, len(chapters), 3):  # 注意：split 的结果会包含分组，所以步长为 3
        chapter_title = chapters[i].strip()  # 章节标题（如 "第1章 引言" 或 "第一章 引言"）
        chapter_content = chapters[i+2].strip()  # 章节内容
        chapter_list.append((chapter_title, chapter_content))

    return chapter_list

def add_css_style(book: epub.EpubBook) -> None:
    """
    添加CSS样式到EPUB书籍。

    :param book: EpubBook对象
    """
    style = '''
    body {
        font-family: "Noto Sans CJK SC", "WenQuanYi Micro Hei", "WenQuanYi Zen Hei", "AR PL UMing", serif;
        font-size: 1em;
        line-height: 1.6;
    }
    h1 {
        font-size: 1.5em;
        text-align: center;
    }
    p {
        text-indent: 2em;
    }
    '''
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style.encode('utf-8'))
    book.add_item(nav_css)

def write_epub_file(epub_file: str, book: epub.EpubBook) -> None:
    """
    将EPUB书籍写入文件。

    :param epub_file: EPUB文件路径
    :param book: EpubBook对象
    """
    try:
        epub.write_epub(epub_file, book, {})
    except Exception as e:
        raise Exception(f"无法写入EPUB文件 {epub_file}: {e}")

def create_chapter(title: str, content: str, file_name: str) -> epub.EpubHtml:
    """
    创建一个EPUB章节。

    :param title: 章节标题（如 "第1章 引言"）
    :param content: 章节内容
    :param file_name: 章节文件名
    :return: EpubHtml对象
    """
    if not content:
        raise ValueError("章节内容不能为空")

    chapter = epub.EpubHtml(title=title, file_name=file_name, lang='zh')  # 设置章节语言为中文
    chapter.content = f'<h1>{title}</h1><p>{content}</p>'
    return chapter
