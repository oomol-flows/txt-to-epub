from typing import Optional, List, NamedTuple

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