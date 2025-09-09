import re
from typing import List
from data_structures import Section, Chapter, Volume


def remove_table_of_contents(content: str) -> str:
    """
    移除文本中的目录部分，避免目录内容干扰正文章节识别。
    
    :param content: 原始文本内容
    :return: 移除目录后的文本内容
    """
    if not content or not content.strip():
        return content
    
    lines = content.split('\n')
    
    # 查找目录开始位置
    toc_start = -1
    toc_end = -1
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        # 识别目录开始：单独一行的"目录"
        if stripped_line == "目录":
            toc_start = i
            continue
            
        # 如果已经找到目录开始，查找目录结束
        if toc_start != -1:
            # 目录结束的条件：
            # 1. 遇到连续的空行（通常目录后面有空行分隔）
            # 2. 遇到明显的正文内容（长段落）
            if not stripped_line:  # 空行
                # 检查后续是否有连续空行或正文开始
                next_non_empty = -1
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip():
                        next_non_empty = j
                        break
                        
                if next_non_empty != -1:
                    next_line = lines[next_non_empty].strip()
                    # 如果下一个非空行是正文内容（长度较长且不是章节标题格式）
                    if (len(next_line) > 30 and 
                        not re.match(r'^第[一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬\d]+[章节卷部篇]\s', next_line)):
                        toc_end = i
                        break
            
            # 如果当前行是明显的正文开始（长段落）
            elif (len(stripped_line) > 50 and 
                  not re.match(r'^第[一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬\d]+[章节]\s', stripped_line) and
                  not re.match(r'^前言$|^序$|^序言$', stripped_line)):
                toc_end = i - 1
                break
    
    # 如果找到了目录，移除目录部分
    if toc_start != -1 and toc_end != -1:
        # 移除目录部分，但保留目录前后的内容
        remaining_lines = lines[:toc_start] + lines[toc_end + 1:]
        return '\n'.join(remaining_lines)
    elif toc_start != -1:
        # 只找到目录开始，可能目录一直到某个明显的章节开始
        for i in range(toc_start + 1, len(lines)):
            line = lines[i].strip()
            # 找到第一个明显的正文章节标题或前言
            if (re.match(r'^第[一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬\d]+章\s+.+', line) or
                line == "前言"):
                remaining_lines = lines[:toc_start] + lines[i:]
                return '\n'.join(remaining_lines)
    
    return content


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
    
    # 预处理：移除目录部分，避免目录干扰正文解析
    content = remove_table_of_contents(content)
    
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
        seen_volume_titles = set()  # 用于跟踪已经见过的卷标题
        for i in range(1, len(volume_parts), 3):
            if i + 2 < len(volume_parts):
                volume_title = volume_parts[i].strip()
                volume_content = volume_parts[i + 2]
                # 检查卷标题是否重复，如果重复则跳过
                if volume_title and volume_title not in seen_volume_titles:
                    seen_volume_titles.add(volume_title)
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
    
    # 匹配章节标题模式（支持数字和中文数字，包括大写中文数字，以及特殊章节类型）
    # 支持：第X章 标题、番外 、番外篇 、外传 、特别篇 、插话 等（特殊标题后必须有且仅有一个空格）
    # 要求章节标题独立成行，避免匹配正文中的章节引用
    chapter_pattern = re.compile(r'(?:^|\n)(\s*(?:第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s+[^\n]+|(?:番外|番外篇|外传|特别篇|插话|后记|尾声|终章|楔子|序章)\s+[^\n]*)\s*)(?=\n|$)', re.MULTILINE)
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
    
    # 新的正则表达式split结果结构：[前内容, 章节标题, 数字分组, 内容, 章节标题, 数字分组, 内容, ...]
    seen_titles = set()  # 用于跟踪已经见过的章节标题
    
    i = 1  # 从第一个匹配的章节标题开始
    while i < len(chapters_raw):
        if i < len(chapters_raw) and chapters_raw[i]:  # 确保有章节标题
            chapter_title = chapters_raw[i].strip()
            
            # 获取章节内容（跳过数字分组，取下一个非空元素）
            content_index = i + 2  # 跳过数字分组
            chapter_content = ""
            
            if content_index < len(chapters_raw):
                chapter_content = chapters_raw[content_index].strip('\n\r')
                
            if chapter_title and chapter_title not in seen_titles:  # 确保章节标题不为空且未重复
                seen_titles.add(chapter_title)
                # 进一步分析章节内容，看是否包含节
                sections = parse_sections_from_content(chapter_content)
                if sections:
                    # 如果有节，章节内容为空（内容都在节中）
                    chapter_list.append(Chapter(title=chapter_title, content="", sections=sections))
                else:
                    # 如果没有节，章节直接包含内容
                    if not chapter_content.strip():
                        chapter_content = "此章节内容为空。"
                    chapter_list.append(Chapter(title=chapter_title, content=chapter_content, sections=[]))
        
        # 移动到下一个章节标题（每次跳过3个元素：标题、数字分组、内容）
        i += 3

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
    seen_titles = set()  # 用于跟踪已经见过的节标题
    for i in range(1, len(sections_raw), 3):
        if i + 2 < len(sections_raw):
            section_title = sections_raw[i].strip()
            section_content = sections_raw[i + 2].strip('\n\r')
            if section_title and section_title not in seen_titles:  # 确保节标题不为空且未重复
                seen_titles.add(section_title)
                # 确保节内容不为空
                if not section_content.strip():
                    section_content = "此节内容为空。"
                section_list.append(Section(title=section_title, content=section_content))
        elif i + 1 < len(sections_raw):  # 处理最后一个节可能缺少内容的情况
            section_title = sections_raw[i].strip()
            if section_title and section_title not in seen_titles:
                seen_titles.add(section_title)
                section_list.append(Section(title=section_title, content="此节内容为空。"))

    return section_list
