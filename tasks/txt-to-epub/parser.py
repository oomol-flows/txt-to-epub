import re
from typing import List
from data_structures import Section, Chapter, Volume


class ChinesePatterns:
    """中文书籍的正则表达式模式"""
    
    # 目录关键词
    TOC_KEYWORDS = ["目录"]
    
    # 前言关键词
    PREFACE_KEYWORDS = ["前言", "序", "序言"]
    
    # Volume/Part/Book patterns
    VOLUME_PATTERN = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})[卷部篇]\s+[^\n]*)')
    
    # Chapter patterns
    CHAPTER_PATTERN = re.compile(r'(?:^|\n)(\s*(?:第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s+[^\n]+|(?:番外|番外篇|外传|特别篇|插话|后记|尾声|终章|楔子|序章)\s+[^\n]*)\s*)(?=\n|$)', re.MULTILINE)
    
    # Section patterns
    SECTION_PATTERN = re.compile(r'(第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})节\s+[^\n]*)')


class EnglishPatterns:
    """英文书籍的正则表达式模式"""
    
    # 目录关键词
    TOC_KEYWORDS = ["Contents", "Table of Contents", "TOC"]
    
    # 前言关键词  
    PREFACE_KEYWORDS = ["Preface", "Foreword", "Introduction", "Prologue"]
    
    # 数字词汇映射
    WORD_TO_NUM = {
        'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
        'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
        'eleven': '11', 'twelve': '12', 'thirteen': '13', 'fourteen': '14', 'fifteen': '15',
        'sixteen': '16', 'seventeen': '17', 'eighteen': '18', 'nineteen': '19', 'twenty': '20'
    }
    
    # 罗马数字映射
    ROMAN_TO_NUM = {
        'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5',
        'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10',
        'XI': '11', 'XII': '12', 'XIII': '13', 'XIV': '14', 'XV': '15',
        'XVI': '16', 'XVII': '17', 'XVIII': '18', 'XIX': '19', 'XX': '20'
    }
    
    # Volume/Part/Book patterns
    VOLUME_PATTERN = re.compile(r'(?:^|\n)(\s*(?:(?:Part|Book|Volume)\s+(?:I{1,3}V?|VI{0,3}|IX|X{1,2}|\d{1,2}|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|Seventeen|Eighteen|Nineteen|Twenty)(?::\s*[^\n]+)?)\s*)(?=\n|$)', re.MULTILINE | re.IGNORECASE)
    
    # Chapter patterns
    CHAPTER_PATTERN = re.compile(r'(?:^|\n)(\s*(?:Chapter|Ch\.?|Chap\.?)\s+(?:I{1,3}V?|VI{0,3}|IX|X{1,2}L?|\d{1,2}|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|Seventeen|Eighteen|Nineteen|Twenty|Thirty|Forty|Fifty)(?::\s*[^\n]+)?\s*)(?=\n|$)', re.MULTILINE | re.IGNORECASE)
    
    # Section patterns
    SECTION_PATTERN = re.compile(r'(?:^|\n)(\s*(?:Section|Sect\.?)\s+(?:\d{1,2}(?:\.\d+)?|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|Seventeen|Eighteen|Nineteen|Twenty)(?::\s*[^\n]+)?\s*)(?=\n|$)', re.MULTILINE | re.IGNORECASE)
    
    # Numbered section patterns (e.g., 1.1, 2.3)
    NUMBERED_SECTION_PATTERN = re.compile(r'(?:^|\n)(\s*(\d+\.\d+)\s+[^\n]+\s*)(?=\n|$)', re.MULTILINE)


def detect_language(content: str) -> str:
    """
    Detect the main language of the text (Chinese or English)
    
    :param content: Text content
    :return: 'chinese' or 'english'
    """
    if not content or not content.strip():
        return 'chinese'  # Default to Chinese
    
    # Count Chinese characters
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    # Count English letters
    english_chars = len(re.findall(r'[a-zA-Z]', content))
    
    # Check common Chinese chapter keywords
    chinese_keywords = ['第', '章', '节', '卷', '部', '篇', '序言', '前言', '目录']
    chinese_keyword_count = sum(content.count(kw) for kw in chinese_keywords)
    
    # Check common English chapter keywords
    english_keywords = ['Chapter', 'Section', 'Part', 'Book', 'Volume', 'Contents', 'Preface', 'Introduction']
    english_keyword_count = sum(content.lower().count(kw.lower()) for kw in english_keywords)
    
    # Decision logic
    if chinese_chars > english_chars * 0.5 or chinese_keyword_count > english_keyword_count:
        return 'chinese'
    else:
        return 'english'


def remove_table_of_contents(content: str, language: str = None) -> str:
    """
    Remove the table of contents section from the text to avoid interference with chapter recognition.
    Supports both Chinese and English table of contents recognition.
    
    :param content: Original text content
    :param language: Language type, 'chinese' or 'english', auto-detect if None
    :return: Text content with table of contents removed
    """
    if not content or not content.strip():
        return content
    
    # Auto-detect language
    if language is None:
        language = detect_language(content)
    
    # Select corresponding patterns
    if language == 'english':
        patterns = EnglishPatterns()
        toc_keywords = patterns.TOC_KEYWORDS
        preface_keywords = patterns.PREFACE_KEYWORDS
        chapter_patterns = [patterns.CHAPTER_PATTERN, patterns.VOLUME_PATTERN]
    else:
        patterns = ChinesePatterns()
        toc_keywords = patterns.TOC_KEYWORDS
        preface_keywords = patterns.PREFACE_KEYWORDS
        chapter_patterns = [patterns.CHAPTER_PATTERN, patterns.VOLUME_PATTERN]
    
    lines = content.split('\n')
    
    # Find table of contents start position
    toc_start = -1
    toc_end = -1
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        # Identify table of contents start: standalone line with TOC keywords
        if stripped_line in toc_keywords or any(keyword.lower() == stripped_line.lower() for keyword in toc_keywords):
            toc_start = i
            continue
            
        # If table of contents start found, look for the end
        if toc_start != -1:
            # Table of contents end conditions:
            # 1. Consecutive empty lines (usually TOC is followed by empty lines)
            # 2. Clear main content (long paragraphs)
            if not stripped_line:  # Empty line
                # Check if there are consecutive empty lines or main content following
                next_non_empty = -1
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip():
                        next_non_empty = j
                        break
                        
                if next_non_empty != -1:
                    next_line = lines[next_non_empty].strip()
                    # If next non-empty line is main content (long and not chapter title format)
                    if len(next_line) > 30:
                        is_chapter = False
                        for pattern in chapter_patterns:
                            if pattern.search(next_line):
                                is_chapter = True
                                break
                        if not is_chapter:
                            toc_end = i
                            break
            
            # If current line is clearly the beginning of main content (long paragraph)
            elif len(stripped_line) > 50:
                is_chapter = False
                is_preface = False
                
                # Check if it's a chapter title
                for pattern in chapter_patterns:
                    if pattern.search(stripped_line):
                        is_chapter = True
                        break
                
                # Check if it's a preface
                if any(keyword.lower() == stripped_line.lower() for keyword in preface_keywords):
                    is_preface = True
                
                if not is_chapter and not is_preface:
                    toc_end = i - 1
                    break
    
    # If table of contents found, remove it
    if toc_start != -1 and toc_end != -1:
        # Remove table of contents but keep content before and after
        remaining_lines = lines[:toc_start] + lines[toc_end + 1:]
        return '\n'.join(remaining_lines)
    elif toc_start != -1:
        # Only found table of contents start, possibly continues until clear chapter beginning
        for i in range(toc_start + 1, len(lines)):
            line = lines[i].strip()
            # Find first clear main content chapter title or preface
            for pattern in chapter_patterns:
                if pattern.search(line):
                    remaining_lines = lines[:toc_start] + lines[i:]
                    return '\n'.join(remaining_lines)
            if any(keyword.lower() == line.lower() for keyword in preface_keywords):
                remaining_lines = lines[:toc_start] + lines[i:]
                return '\n'.join(remaining_lines)
    
    return content


def parse_hierarchical_content(content: str) -> List[Volume]:
    """
    Split text content into three-level hierarchical structure: volumes, chapters, sections.
    Supports both Chinese and English book formats.

    :param content: Text content
    :return: List of volumes containing complete hierarchical structure
    """
    if not content or not content.strip():
        # If content is empty, return a volume with empty chapter
        return [Volume(title=None, chapters=[Chapter(title="Empty Content", content="This document is empty or cannot be parsed.", sections=[])])]
    
    # Detect language
    language = detect_language(content)
    
    # Preprocessing: remove table of contents to avoid interference with content parsing
    content = remove_table_of_contents(content, language)
    
    # Select corresponding patterns based on language
    if language == 'english':
        patterns = EnglishPatterns()
        volume_pattern = patterns.VOLUME_PATTERN
    else:
        patterns = ChinesePatterns() 
        volume_pattern = patterns.VOLUME_PATTERN
    
    # First split by volumes
    volume_parts = volume_pattern.split(content)
    
    volumes = []
    
    if len(volume_parts) == 1:
        # 没有卷，只有章节
        chapters = parse_chapters_from_content(volume_parts[0], language)
        if chapters:
            volumes.append(Volume(title=None, chapters=chapters))
        else:
            # 如果没有识别到章节，将整个内容作为一个章节
            default_title = "正文" if language == 'chinese' else "Content"
            volumes.append(Volume(title=None, chapters=[Chapter(title=default_title, content=volume_parts[0].strip(), sections=[])]))
    else:
        # 处理第一部分（可能是序言等，没有卷标题的内容）
        if volume_parts[0].strip():
            pre_chapters = parse_chapters_from_content(volume_parts[0], language)
            if pre_chapters:
                volumes.append(Volume(title=None, chapters=pre_chapters))
            else:
                # 如果第一部分没有章节结构，作为序言章节
                preface_title = "序言" if language == 'chinese' else "Preface"
                volumes.append(Volume(title=None, chapters=[Chapter(title=preface_title, content=volume_parts[0].strip(), sections=[])]))
        
        # 处理有卷标题的部分，步长取决于正则表达式的分组数
        step = 3 if language == 'chinese' else 2  # 英文模式分组较少
        seen_volume_titles = set()  # 用于跟踪已经见过的卷标题
        for i in range(1, len(volume_parts), step):
            content_index = i + (step - 1)
            if content_index < len(volume_parts):
                volume_title = volume_parts[i].strip()
                volume_content = volume_parts[content_index]
                # 检查卷标题是否重复，如果重复则跳过
                if volume_title and volume_title not in seen_volume_titles:
                    seen_volume_titles.add(volume_title)
                    chapters = parse_chapters_from_content(volume_content, language)
                    if chapters:
                        volumes.append(Volume(title=volume_title, chapters=chapters))
                    elif volume_content.strip():  # 如果有内容但没有章节结构
                        # 将整个卷内容作为一个章节
                        default_title = "正文" if language == 'chinese' else "Content"
                        volumes.append(Volume(title=volume_title, chapters=[Chapter(title=default_title, content=volume_content.strip(), sections=[])]))

    # 确保至少有一个卷
    if not volumes:
        error_title = "未知内容" if language == 'chinese' else "Unknown Content"
        error_content = "无法解析文档结构，请检查文档格式。" if language == 'chinese' else "Unable to parse document structure. Please check document format."
        volumes.append(Volume(title=None, chapters=[Chapter(title=error_title, content=error_content, sections=[])]))

    return volumes


def parse_chapters_from_content(content: str, language: str = 'chinese') -> List[Chapter]:
    """
    Split chapters and sections from given content.
    Supports both Chinese and English chapter formats.

    :param content: Text content
    :param language: Language type, 'chinese' or 'english'
    :return: Chapter list, each chapter contains title, content and section list
    """
    if not content or not content.strip():
        return []
    
    # Select corresponding patterns based on language
    if language == 'english':
        patterns = EnglishPatterns()
        chapter_pattern = patterns.CHAPTER_PATTERN
        preface_keywords = patterns.PREFACE_KEYWORDS
    else:
        patterns = ChinesePatterns()
        chapter_pattern = patterns.CHAPTER_PATTERN
        preface_keywords = patterns.PREFACE_KEYWORDS
    
    chapters_raw = chapter_pattern.split(content)

    chapter_list = []
    
    # If no chapter titles found, return empty list (let parent function handle)
    if len(chapters_raw) == 1:
        return chapter_list
    
    # Process first part (possibly preface content without chapter title)
    if chapters_raw[0].strip():
        # Treat preface content as untitled chapter
        sections = parse_sections_from_content(chapters_raw[0], language)
        preface_title = "前言" if language == 'chinese' else "Preface"
        if sections:
            chapter_list.append(Chapter(title=preface_title, content="", sections=sections))
        else:
            chapter_list.append(Chapter(title=preface_title, content=chapters_raw[0].strip(), sections=[]))
    
    # 根据语言确定split结果的步长
    # 中文模式：[前内容, 章节标题, 数字分组, 内容, ...]  步长=3
    # 英文模式：[前内容, 章节标题, 内容, ...] 步长=2  
    step = 3 if language == 'chinese' else 2
    seen_titles = set()  # 用于跟踪已经见过的章节标题
    
    i = 1  # 从第一个匹配的章节标题开始
    while i < len(chapters_raw):
        if i < len(chapters_raw) and chapters_raw[i]:  # 确保有章节标题
            chapter_title = chapters_raw[i].strip()
            
            # 获取章节内容
            content_index = i + (step - 1)
            chapter_content = ""
            
            if content_index < len(chapters_raw):
                chapter_content = chapters_raw[content_index].strip('\n\r')
                
            if chapter_title and chapter_title not in seen_titles:  # 确保章节标题不为空且未重复
                seen_titles.add(chapter_title)
                # 进一步分析章节内容，看是否包含节
                sections = parse_sections_from_content(chapter_content, language)
                if sections:
                    # 如果有节，章节内容为空（内容都在节中）
                    chapter_list.append(Chapter(title=chapter_title, content="", sections=sections))
                else:
                    # 如果没有节，章节直接包含内容
                    if not chapter_content.strip():
                        empty_content = "此章节内容为空。" if language == 'chinese' else "This chapter is empty."
                        chapter_content = empty_content
                    chapter_list.append(Chapter(title=chapter_title, content=chapter_content, sections=[]))
        
        # 移动到下一个章节标题
        i += step

    return chapter_list


def parse_sections_from_content(content: str, language: str = 'chinese') -> List[Section]:
    """
    从给定的章节内容中分割出节。
    支持中英文节格式。

    :param content: 章节内容
    :param language: 语言类型，'chinese' 或 'english'
    :return: 节列表，每个节包含标题和内容
    """
    if not content or not content.strip():
        return []
    
    # 根据语言选择对应的模式
    if language == 'english':
        patterns = EnglishPatterns()
        # 英文尝试多种节模式
        section_patterns = [patterns.SECTION_PATTERN, patterns.NUMBERED_SECTION_PATTERN]
    else:
        patterns = ChinesePatterns()
        section_patterns = [patterns.SECTION_PATTERN]

    section_list = []
    sections_raw = None
    active_pattern = None
    
    # 尝试不同的节模式
    for pattern in section_patterns:
        sections_raw = pattern.split(content)
        if len(sections_raw) > 1:  # 找到匹配的模式
            active_pattern = pattern
            break
    
    # 如果没有找到节模式，返回空列表
    if sections_raw is None or len(sections_raw) == 1:
        return section_list
    
    # 处理第一部分（章节序言，没有节标题的内容）
    if sections_raw[0].strip():
        preface_title = "章节序言" if language == 'chinese' else "Chapter Preface"
        section_list.append(Section(title=preface_title, content=sections_raw[0].strip()))
    
    # 根据模式和语言确定步长
    if language == 'english' and active_pattern == patterns.NUMBERED_SECTION_PATTERN:
        step = 3  # 数字编号模式有分组
    elif language == 'english':
        step = 2  # 普通英文模式
    else:
        step = 3  # 中文模式有分组
    
    seen_titles = set()  # 用于跟踪已经见过的节标题
    for i in range(1, len(sections_raw), step):
        content_index = i + (step - 1)
        if content_index < len(sections_raw):
            section_title = sections_raw[i].strip()
            section_content = sections_raw[content_index].strip('\n\r')
            if section_title and section_title not in seen_titles:  # 确保节标题不为空且未重复
                seen_titles.add(section_title)
                # 确保节内容不为空
                if not section_content.strip():
                    empty_content = "此节内容为空。" if language == 'chinese' else "This section is empty."
                    section_content = empty_content
                section_list.append(Section(title=section_title, content=section_content))
        elif i + 1 < len(sections_raw):  # 处理最后一个节可能缺少内容的情况
            section_title = sections_raw[i].strip()
            if section_title and section_title not in seen_titles:
                seen_titles.add(section_title)
                empty_content = "此节内容为空。" if language == 'chinese' else "This section is empty."
                section_list.append(Section(title=section_title, content=empty_content))

    return section_list
