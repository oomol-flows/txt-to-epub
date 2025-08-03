from typing import List, Tuple, Optional
from .data_structures import Volume, Chapter
from .parser import parse_hierarchical_content, parse_chapters_from_content


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