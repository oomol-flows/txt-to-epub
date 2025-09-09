#!/usr/bin/env python3

"""
验证修复效果 - 确认正文引用不被误识别为章节标题
"""

import re
import sys
import os
sys.path.append('/app/workspace/tasks/txt-to-epub')

from parser import remove_table_of_contents

def main():
    """验证修复效果"""
    
    test_file = "/oomol-driver/oomol-storage/book/伯特兰·罗素：哲学问题.txt"
    
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除目录
    content = remove_table_of_contents(content)
    
    # 新的章节匹配模式
    chapter_pattern = re.compile(r'(?:^|\n)(\s*(?:第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s+[^\n]+|(?:番外|番外篇|外传|特别篇|插话|后记|尾声|终章|楔子|序章)\s+[^\n]*)\s*)(?=\n|$)', re.MULTILINE)
    
    # 获取所有匹配
    matches = chapter_pattern.findall(content)
    
    print("=== 修复效果验证 ===")
    print(f"✅ 正确识别的章节标题数量: {len(matches)}")
    
    # 检查是否包含问题引用
    problem_phrases = [
        "应当记得，在第十一章结束时",
        "在第十一章结束时",
        "第十一章结束时"
    ]
    
    found_problem = False
    for i, match in enumerate(matches):
        title = match[0].strip()
        # 检查章节标题是否包含问题短语
        for phrase in problem_phrases:
            if phrase in title:
                print(f"❌ 发现问题！章节 {i+1} 包含引用: '{title}'")
                found_problem = True
                break
    
    if not found_problem:
        print("✅ 未发现正文引用被误识别为章节标题")
    
    # 显示所有章节标题
    print(f"\n正确识别的章节标题:")
    for i, match in enumerate(matches):
        title = match[0].strip()
        print(f"{i+1:2}: {title}")
    
    # 验证问题句子确实存在于正文中，但没被当作章节标题
    target_sentence = "应当记得，在第十一章结束时，我们曾提出可能有两种自明性"
    if target_sentence in content:
        print(f"\n✅ 问题句子存在于正文中（这是正确的）")
        # 找到这个句子在哪个章节中
        split_result = chapter_pattern.split(content)
        
        sentence_pos = content.find(target_sentence)
        chapter_found = False
        
        # 查找句子属于哪个章节
        for i in range(1, len(split_result), 3):
            if i + 2 < len(split_result):
                chapter_title = split_result[i].strip()
                chapter_content = split_result[i + 2]
                
                if target_sentence in chapter_content:
                    print(f"✅ 问题句子正确地属于章节: '{chapter_title}'")
                    chapter_found = True
                    break
        
        if not chapter_found:
            print("❌ 未找到问题句子所属章节")
    else:
        print("❌ 未在正文中找到问题句子")

if __name__ == "__main__":
    main()