#!/usr/bin/env python3

"""
测试英文书籍支持功能
"""

import sys
import os
sys.path.append('/app/workspace/tasks/txt-to-epub')

from data_structures import Section, Chapter, Volume
from parser import detect_language, parse_hierarchical_content, remove_table_of_contents

def test_language_detection():
    """测试语言检测功能"""
    print("=== 测试语言检测功能 ===")
    
    # 测试中文文本
    chinese_file = "/oomol-driver/oomol-storage/book/伯特兰·罗素：哲学问题.txt"
    with open(chinese_file, 'r', encoding='utf-8') as f:
        chinese_content = f.read()[:1000]  # 只取前1000字符
    
    chinese_lang = detect_language(chinese_content)
    print(f"中文文本检测结果: {chinese_lang}")
    
    # 测试英文文本
    english_file = "/oomol-driver/oomol-storage/book/Pride_and_Prejudice_Sample.txt"
    with open(english_file, 'r', encoding='utf-8') as f:
        english_content = f.read()[:1000]  # 只取前1000字符
    
    english_lang = detect_language(english_content)
    print(f"英文文本检测结果: {english_lang}")
    
    return chinese_lang == 'chinese' and english_lang == 'english'

def test_english_toc_removal():
    """测试英文目录移除功能"""
    print("\n=== 测试英文目录移除功能 ===")
    
    english_file = "/oomol-driver/oomol-storage/book/Pride_and_Prejudice_Sample.txt"
    with open(english_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"原文本长度: {len(content)} 字符")
    
    # 移除目录
    content_without_toc = remove_table_of_contents(content, 'english')
    print(f"移除目录后长度: {len(content_without_toc)} 字符")
    
    # 检查目录是否被移除
    has_contents = "Contents" in content_without_toc
    print(f"移除目录后是否还包含'Contents': {has_contents}")
    
    # 显示移除目录后的文本开头
    lines = content_without_toc.split('\n')[:15]
    print("\n移除目录后的文本开头:")
    for i, line in enumerate(lines, 1):
        if line.strip():
            print(f"{i:2}: {line}")
    
    return not has_contents

def test_english_parsing():
    """测试英文书籍解析功能"""
    print("\n=== 测试英文书籍解析功能 ===")
    
    english_file = "/oomol-driver/oomol-storage/book/Pride_and_Prejudice_Sample.txt"
    with open(english_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析层次结构
    volumes = parse_hierarchical_content(content)
    
    print(f"解析出的卷数: {len(volumes)}")
    
    success = True
    
    for vol_idx, volume in enumerate(volumes):
        vol_title = volume.title if volume.title else f"Volume {vol_idx+1}"
        print(f"\n{vol_title}: {len(volume.chapters)} 章")
        
        for chap_idx, chapter in enumerate(volume.chapters):
            print(f"  第{chap_idx+1}章: {chapter.title}")
            if chapter.content:
                content_preview = chapter.content[:100].replace('\n', ' ')
                print(f"    内容预览: {content_preview}...")
            if chapter.sections:
                print(f"    包含 {len(chapter.sections)} 个节")
                for sec_idx, section in enumerate(chapter.sections[:2]):  # 只显示前2节
                    print(f"      {sec_idx+1}. {section.title}")
    
    # 验证关键结构
    expected_parts = ["Part I: First Impressions", "Part II: Growing Attachments"]
    expected_chapters = ["Chapter 1: Mr. Bennet and His Daughters", "Chapter 2: The Arrival of Mr. Bingley"]
    
    # 检查是否正确识别了Part
    found_parts = []
    found_chapters = []
    
    for volume in volumes:
        if volume.title and any(part in volume.title for part in expected_parts):
            found_parts.append(volume.title)
        for chapter in volume.chapters:
            if any(chap in chapter.title for chap in expected_chapters):
                found_chapters.append(chapter.title)
    
    print(f"\n✅ 验证结果:")
    print(f"找到的Part数量: {len(found_parts)}")
    print(f"找到的预期章节数量: {len(found_chapters)}")
    
    if len(found_parts) >= 2 and len(found_chapters) >= 2:
        print("✅ 英文书籍解析成功！")
    else:
        print("❌ 英文书籍解析存在问题")
        success = False
    
    return success

def test_section_parsing():
    """测试英文节解析"""
    print("\n=== 测试英文节解析功能 ===")
    
    # 创建包含节的测试内容
    test_content = """
Chapter 1: Test Chapter

This is the chapter introduction.

Section 1: First Section

This is the content of the first section. It contains some important information about the topic at hand.

Section 2: Second Section  

This is the content of the second section. It continues the discussion from the previous section.

1.1 Numbered Section

This is content under a numbered section format.

1.2 Another Numbered Section

More content under numbered format.
"""
    
    from parser import parse_chapters_from_content
    chapters = parse_chapters_from_content(test_content, 'english')
    
    if chapters:
        chapter = chapters[0]
        print(f"章节标题: {chapter.title}")
        print(f"节数量: {len(chapter.sections)}")
        
        for i, section in enumerate(chapter.sections):
            print(f"  节{i+1}: {section.title}")
            content_preview = section.content[:50].replace('\n', ' ')
            print(f"    内容: {content_preview}...")
        
        return len(chapter.sections) > 0
    else:
        print("❌ 未能解析出章节")
        return False

def main():
    """主测试函数"""
    print("开始测试英文书籍支持功能...\n")
    
    tests = [
        ("语言检测", test_language_detection),
        ("英文目录移除", test_english_toc_removal), 
        ("英文书籍解析", test_english_parsing),
        ("英文节解析", test_section_parsing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n{test_name}: ❌ 异常 - {e}")
            import traceback
            traceback.print_exc()
    
    # 总结
    print(f"\n{'='*50}")
    print("测试总结:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n通过: {passed}/{total} 测试")
    
    if passed == total:
        print("🎉 所有测试通过！英文书籍支持功能正常工作。")
    else:
        print("⚠️  部分测试失败，需要进一步调试。")

if __name__ == "__main__":
    main()