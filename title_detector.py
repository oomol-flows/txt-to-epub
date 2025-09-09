#!/usr/bin/env python3

"""
标题检测器 - 专门用于检测和移除目录，避免干扰正文解析
"""

import sys
import os
sys.path.append('/app/workspace/tasks/txt-to-epub')

from data_structures import Section, Chapter, Volume
from parser import remove_table_of_contents

def main():
    """演示目录移除功能"""
    
    test_file = "/oomol-driver/oomol-storage/book/伯特兰·罗素：哲学问题.txt"
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("原文本片段:")
        print(content[400:800])
        print("\n" + "="*50)
        
        # 移除目录
        content_without_toc = remove_table_of_contents(content)
        
        print("移除目录后的文本片段:")
        print(content_without_toc[400:800])
        print(f"\n✅ 目录已成功移除！文本长度从 {len(content)} 减少到 {len(content_without_toc)}")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")

if __name__ == "__main__":
    main()