#!/usr/bin/env python3

"""
测试目录移除和章节解析功能
"""

import sys
import os
sys.path.append('/app/workspace')
sys.path.append('/app/workspace/tasks/txt-to-epub')

from data_structures import Section, Chapter, Volume
from parser import remove_table_of_contents, parse_hierarchical_content

def test_toc_removal():
    """测试目录移除功能"""
    
    # 读取罗素哲学问题文本
    test_file = "/oomol-driver/oomol-storage/book/伯特兰·罗素：哲学问题.txt"
    
    print("=== 测试目录移除功能 ===")
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"原文本长度: {len(content)} 字符")
        
        # 移除目录
        content_without_toc = remove_table_of_contents(content)
        print(f"移除目录后长度: {len(content_without_toc)} 字符")
        
        # 显示移除目录后的开头部分
        lines = content_without_toc.split('\n')[:30]
        print("\n移除目录后的文本开头:")
        for i, line in enumerate(lines, 1):
            if line.strip():
                print(f"{i:2}: {line}")
        
        return content_without_toc
        
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

def test_chapter_parsing(content):
    """测试章节解析功能"""
    
    print("\n=== 测试章节解析功能 ===")
    
    try:
        volumes = parse_hierarchical_content(content)
        print(f"解析出的卷数: {len(volumes)}")
        
        for vol_idx, volume in enumerate(volumes):
            vol_title = volume.title if volume.title else f"卷{vol_idx+1}"
            print(f"\n{vol_title}: {len(volume.chapters)} 章")
            
            for chap_idx, chapter in enumerate(volume.chapters[:5]):  # 只显示前5章
                print(f"  第{chap_idx+1}章: {chapter.title}")
                if chapter.content:
                    content_preview = chapter.content[:100].replace('\n', ' ')
                    print(f"    内容预览: {content_preview}...")
                if chapter.sections:
                    print(f"    包含 {len(chapter.sections)} 个节")
                    
        return volumes
        
    except Exception as e:
        print(f"章节解析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("开始测试目录匹配修复...")
    
    # 测试目录移除
    content = test_toc_removal()
    if not content:
        return
    
    # 测试章节解析
    volumes = test_chapter_parsing(content)
    
    if volumes:
        print(f"\n✅ 测试完成！成功解析出 {len(volumes)} 卷，包含章节总数: {sum(len(v.chapters) for v in volumes)}")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main()