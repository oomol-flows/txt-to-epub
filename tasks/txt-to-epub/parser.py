import re
from typing import List
from .data_structures import Section, Chapter, Volume


def parse_hierarchical_content(content: str) -> List[Volume]:
    """
    将文本内容分割成卷、章、节的三级层次结构。
    支持"卷"、"部"、"篇"作为同一层级的单位。

    :param content: 文本内容
    :return: 卷列表，包含完整的层次结构
    """
    if not content or not content.strip():
        # 如果内容为空，返回一个包含空章节的卷
        return [Volume(title=None, chapters=[Chapter(title="空白内容", content="此文档内容为空或无法解析。", sections=[])])]
    
    # 匹配卷/部/篇标题模式（支持数字和中文数字，包括大写中文数字）
    volume_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})[卷部篇]\s+[^\n]*)')
    
    # 首先按卷分割
    volume_parts = volume_pattern.split(content)
    
    volumes = []
    
    if len(volume_parts) == 1:
        # 没有卷，只有章节
        chapters = parse_chapters_from_content(volume_parts[0])
        if chapters:
            volumes.append(Volume(title=None, chapters=chapters))
        else:
            # 如果没有识别到章节，将整个内容作为一个章节
            volumes.append(Volume(title=None, chapters=[Chapter(title="正文", content=volume_parts[0].strip(), sections=[])]))
    else:
        # 处理第一部分（可能是序言等，没有卷标题的内容）
        if volume_parts[0].strip():
            pre_chapters = parse_chapters_from_content(volume_parts[0])
            if pre_chapters:
                volumes.append(Volume(title=None, chapters=pre_chapters))
            else:
                # 如果第一部分没有章节结构，作为序言章节
                volumes.append(Volume(title=None, chapters=[Chapter(title="序言", content=volume_parts[0].strip(), sections=[])]))
        
        # 处理有卷标题的部分，步长为3（因为split会产生分组）
        for i in range(1, len(volume_parts), 3):
            if i + 2 < len(volume_parts):
                volume_title = volume_parts[i].strip()
                volume_content = volume_parts[i + 2]
                chapters = parse_chapters_from_content(volume_content)
                if chapters:
                    volumes.append(Volume(title=volume_title, chapters=chapters))
                elif volume_content.strip():  # 如果有内容但没有章节结构
                    # 将整个卷内容作为一个章节
                    volumes.append(Volume(title=volume_title, chapters=[Chapter(title="正文", content=volume_content.strip(), sections=[])]))

    # 确保至少有一个卷
    if not volumes:
        volumes.append(Volume(title=None, chapters=[Chapter(title="未知内容", content="无法解析文档结构，请检查文档格式。", sections=[])]))

    return volumes


def parse_chapters_from_content(content: str) -> List[Chapter]:
    """
    从给定的内容中分割出章节和节。

    :param content: 文本内容
    :return: 章节列表，每个章节包含标题、内容和节列表
    """
    if not content or not content.strip():
        return []
    
    # 匹配章节标题模式（支持数字和中文数字，包括大写中文数字）
    chapter_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s+[^\n]*)')
    chapters_raw = chapter_pattern.split(content)

    chapter_list = []
    
    # 如果没有找到章节标题，返回空列表（让上级函数处理）
    if len(chapters_raw) == 1:
        return chapter_list
    
    # 处理第一部分（可能是没有章节标题的前言内容）
    if chapters_raw[0].strip():
        # 将前言内容作为一个无标题章节
        sections = parse_sections_from_content(chapters_raw[0])
        if sections:
            chapter_list.append(Chapter(title="前言", content="", sections=sections))
        else:
            chapter_list.append(Chapter(title="前言", content=chapters_raw[0].strip(), sections=[]))
    
    # split结果包含分组，so步长为3
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
        elif i + 1 < len(chapters_raw):  # 处理最后一个章节可能缺少内容的情况
            chapter_title = chapters_raw[i].strip()
            if chapter_title:
                chapter_list.append(Chapter(title=chapter_title, content="此章节内容为空。", sections=[]))

    return chapter_list


def parse_sections_from_content(content: str) -> List[Section]:
    """
    从给定的章节内容中分割出节。

    :param content: 章节内容
    :return: 节列表，每个节包含标题和内容
    """
    if not content or not content.strip():
        return []
    
    # 匹配节标题模式（支持数字和中文数字，包括大写中文数字）
    section_pattern = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})节\s+[^\n]*)')
    sections_raw = section_pattern.split(content)

    section_list = []
    if len(sections_raw) == 1:
        # 没有节标题，返回空列表
        return section_list
    
    # 处理第一部分（章节序言，没有节标题的内容）
    if sections_raw[0].strip():
        section_list.append(Section(title="章节序言", content=sections_raw[0].strip()))
    
    # split结果包含分组，所以步长为3
    for i in range(1, len(sections_raw), 3):
        if i + 2 < len(sections_raw):
            section_title = sections_raw[i].strip()
            section_content = sections_raw[i + 2].strip('\n\r')
            if section_title:  # 确保节标题不为空
                # 确保节内容不为空
                if not section_content.strip():
                    section_content = "此节内容为空。"
                section_list.append(Section(title=section_title, content=section_content))
        elif i + 1 < len(sections_raw):  # 处理最后一个节可能缺少内容的情况
            section_title = sections_raw[i].strip()
            if section_title:
                section_list.append(Section(title=section_title, content="此节内容为空。"))

    return section_list
