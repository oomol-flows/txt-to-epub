# 从拆分的模块中导入所有公共API
from .data_structures import Section, Chapter, Volume
from .core import main, txt_to_epub
from .parser import parse_hierarchical_content, parse_chapters_from_content, parse_sections_from_content
from .legacy import split_into_volumes_and_chapters, split_chapters_from_content, split_into_chapters
from .html_generator import create_volume_page, create_chapter_page, create_section_page, create_chapter
from .css import add_css_style
from .utils import create_epub_book, set_cover_image, read_txt_file, write_epub_file

# 保持向后兼容性的导出
__all__ = [
    'Section', 'Chapter', 'Volume',
    'main', 'txt_to_epub',
    'parse_hierarchical_content', 'parse_chapters_from_content', 'parse_sections_from_content',
    'split_into_volumes_and_chapters', 'split_chapters_from_content', 'split_into_chapters',
    'create_volume_page', 'create_chapter_page', 'create_section_page', 'create_chapter',
    'add_css_style',
    'create_epub_book', 'set_cover_image', 'read_txt_file', 'write_epub_file'
]
