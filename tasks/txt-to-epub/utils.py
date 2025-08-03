import os
import logging
import chardet
from typing import Optional
from ebooklib import epub

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def write_epub_file(epub_file: str, book: epub.EpubBook) -> None:
    """写入EPUB文件。"""
    try:
        epub.write_epub(epub_file, book, {})
        logger.info(f"成功生成EPUB文件: {epub_file}")
    except Exception as e:
        raise Exception(f"无法写入EPUB文件 {epub_file}: {e}")