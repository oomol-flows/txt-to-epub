#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试文字数量验证功能的简单脚本
"""

import sys
from pathlib import Path

# 添加任务路径
task_path = Path(__file__).parent / "tasks" / "txt-to-epub"
sys.path.insert(0, str(task_path))

from word_count_validator import WordCountValidator
from data_structures import Volume, Chapter, Section


def test_validation_with_analysis():
    """测试验证功能和原因分析"""
    
    # 创建测试数据
    original_text = """第一章 测试章节

这是一个测试文档，包含中文字符、English text、数字123，以及标点符号：！？。

第二章 另一个章节

More content here with mixed 中英文 content for testing purposes.
包含各种字符类型的测试内容。"""

    # 模拟转换后的内容（稍有差异）
    volumes = [
        Volume(
            title=None,
            chapters=[
                Chapter(
                    title="第一章 测试章节",
                    content="这是一个测试文档，包含中文字符、English text、数字123，以及标点符号：！？。",
                    sections=[]
                ),
                Chapter(
                    title="第二章 另一个章节", 
                    content="More content here with mixed 中英文 content for testing purposes.\n包含各种字符类型的测试内容。",
                    sections=[]
                )
            ]
        )
    ]
    
    # 创建验证器
    validator = WordCountValidator()
    
    print("=" * 60)
    print("文字数量验证和原因分析测试")
    print("=" * 60)
    
    # 分析原始内容
    validator.analyze_original_content(original_text)
    
    # 分析转换后内容
    validator.analyze_converted_content(volumes)
    
    # 生成完整报告
    report = validator.generate_validation_report()
    print(report)
    
    # 测试变化原因分析
    print("\n" + "=" * 40)
    print("详细原因分析测试")
    print("=" * 40)
    
    analysis = validator.analyze_content_changes()
    for key, value in analysis.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    test_validation_with_analysis()
