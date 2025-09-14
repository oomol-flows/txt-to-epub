#!/usr/bin/env python3

import re
import sys
import os
sys.path.append('/app/workspace/tasks/txt-to-epub')

from parser import remove_table_of_contents

def test_regex():
    """测试章节匹配正则表达式"""
    
    test_file = "/oomol-driver/oomol-storage/book/伯特兰·罗素：哲学问题.txt"
    
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除目录
    content = remove_table_of_contents(content)
    
    # 当前使用的模式
    chapter_pattern = re.compile(r'(?:^|\n)(\s*(?:第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s+[^\n]+|(?:番外|番外篇|外传|特别篇|插话|后记|尾声|终章|楔子|序章)\s+[^\n]*)\s*)(?=\n|$)', re.MULTILINE)
    
    # 找到所有匹配
    matches = chapter_pattern.findall(content)
    print(f"找到 {len(matches)} 个章节标题匹配:")
    
    for i, match in enumerate(matches):
        title = match[0].strip() if match[0] else ""
        print(f"{i+1:2}: '{title}'")
    
    # 查找问题句子附近的内容
    target = "应当记得，在第十一章结束时"
    if target in content:
        pos = content.find(target)
        # 获取前后各100个字符的上下文
        start = max(0, pos - 100)
        end = min(len(content), pos + 200)
        context = content[start:end]
        
        print(f"\n问题句子的上下文:")
        print(f"'{context}'")
        
        # 检查这部分文本是否被正则表达式匹配
        context_matches = chapter_pattern.findall(context)
        if context_matches:
            print(f"在上下文中找到匹配: {context_matches}")
        else:
            print("在上下文中未找到匹配")
    
    # 检查split的结果
    split_result = chapter_pattern.split(content)
    print(f"\nSplit结果长度: {len(split_result)}")
    
    # 显示前几个元素
    for i, part in enumerate(split_result[:10]):
        if part:
            preview = part[:100].replace('\n', '\\n')
            print(f"split[{i}]: '{preview}...'")

if __name__ == "__main__":
    test_regex()