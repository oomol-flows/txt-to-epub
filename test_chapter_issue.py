#!/usr/bin/env python3

"""
测试章节识别问题 - 检查正文引用是否被误识别为章节
"""

import sys
import os
sys.path.append('/app/workspace/tasks/txt-to-epub')

from data_structures import Section, Chapter, Volume
from parser import remove_table_of_contents, parse_hierarchical_content

def main():
    """测试章节识别问题"""
    
    test_file = "/oomol-driver/oomol-storage/book/伯特兰·罗素：哲学问题.txt"
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除目录
        content_without_toc = remove_table_of_contents(content)
        
        # 解析章节
        volumes = parse_hierarchical_content(content_without_toc)
        
        print("章节解析结果:")
        for vol_idx, volume in enumerate(volumes):
            vol_title = volume.title if volume.title else f"卷{vol_idx+1}"
            print(f"\n{vol_title}: 共{len(volume.chapters)}章")
            
            for chap_idx, chapter in enumerate(volume.chapters):
                print(f"  第{chap_idx+1}章: {chapter.title}")
                
                # 检查是否包含问题句子
                if "应当记得，在第十一章结束时" in chapter.content:
                    print(f"    ❌ 发现问题：这章包含了正文引用句子")
                    print(f"    内容开头: {chapter.content[:200]}...")
                
                # 显示每章内容的长度
                content_len = len(chapter.content)
                sections_count = len(chapter.sections)
                print(f"    内容长度: {content_len} 字符, {sections_count} 节")
                
        # 直接在原文中搜索问题句子的位置
        target_sentence = "应当记得，在第十一章结束时，我们曾提出可能有两种自明性"
        if target_sentence in content_without_toc:
            pos = content_without_toc.find(target_sentence)
            # 找到这句话前后的文本
            context_start = max(0, pos - 200)
            context_end = min(len(content_without_toc), pos + len(target_sentence) + 200)
            context = content_without_toc[context_start:context_end]
            
            print(f"\n问题句子的上下文:")
            print(f"位置: {pos}")
            print(f"上下文: ...{context}...")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()