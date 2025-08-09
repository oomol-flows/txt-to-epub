#!/usr/bin/env python3
"""
测试Markdown格式的验证报告生成
"""

import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tasks', 'txt-to-epub'))

from word_count_validator import WordCountValidator
from data_structures import Volume, Chapter, Section

def test_markdown_report():
    """测试Markdown格式的验证报告"""
    
    # 创建测试数据
    validator = WordCountValidator()
    
    # 模拟原始内容
    original_content = """这是一个测试文档。
    
第一章 开始
这是第一章的内容，包含了一些中文文字和English words。
还有一些标点符号！？。

第二章 继续
这是第二章的内容，同样包含中英文混合内容。
Test content with numbers 123 and symbols @#$。
"""
    
    # 模拟转换后的内容结构
    chapter1 = Chapter(
        title="第一章 开始",
        content="这是第一章的内容，包含了一些中文文字和English words。\n还有一些标点符号！？。",
        sections=[]
    )
    
    chapter2 = Chapter(
        title="第二章 继续", 
        content="这是第二章的内容，同样包含中英文混合内容。\nTest content with numbers 123 and symbols @#$。",
        sections=[]
    )
    
    volume = Volume(
        title="测试书籍",
        chapters=[chapter1, chapter2]
    )
    
    volumes = [volume]
    
    # 分析内容
    validator.analyze_original_content(original_content)
    validator.analyze_converted_content(volumes)
    
    # 生成Markdown报告
    markdown_report = validator.generate_validation_report()
    
    print("=== Markdown验证报告 ===")
    print(markdown_report)
    print("\n=== 报告结束 ===")
    
    # 验证是否包含Markdown元素
    assert "# TXT转EPUB文字内容完整性验证报告" in markdown_report
    assert "| 项目 | 转换前 | 转换后 | 差异 | 丢失率 |" in markdown_report
    assert "|------|--------|--------|------|--------|" in markdown_report
    assert "## 📊 转换前后对比" in markdown_report
    assert "## ✅ 验证结果：通过" in markdown_report or "## ❌ 验证结果：失败" in markdown_report
    
    print("\n✅ Markdown格式验证通过！")

if __name__ == "__main__":
    test_markdown_report()
