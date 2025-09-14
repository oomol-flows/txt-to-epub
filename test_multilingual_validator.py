#!/usr/bin/env python3
"""
Test script for multilingual word count validator functionality
"""

import sys
import os
sys.path.append('/app/workspace/tasks/txt-to-epub')

# Create mock data structures for testing
class Section:
    def __init__(self, title="", content=""):
        self.title = title
        self.content = content

class Chapter:
    def __init__(self, title="", content="", sections=None):
        self.title = title
        self.content = content
        self.sections = sections or []

class Volume:
    def __init__(self, title="", chapters=None):
        self.title = title
        self.chapters = chapters or []

# Now create a simplified version of the validator for testing
import re
import logging
from typing import Dict, List, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_chinese_book():
    """Test with Chinese content"""
    print("=== Testing Chinese Book ===")
    
    # Sample Chinese text
    chinese_content = """
    第一章 开始
    
    这是一本中文小说的开头。主人公叫做张三，他住在北京的一个小胡同里。
    每天早上，张三都会到附近的公园里跑步。今天也不例外。
    
    第二章 发现
    
    在公园里，张三发现了一个奇怪的现象。所有的树叶都变成了金色，
    就像童话故事中描述的那样神奇。他停下脚步，仔细观察着这个美丽的景象。
    """
    
    validator = WordCountValidator()
    
    # Analyze original content
    original_stats = validator.analyze_original_content(chinese_content)
    print(f"Detected language: {validator.detected_language}")
    
    # Create mock converted content (slightly different)
    volumes = [
        Volume(
            title="测试卷",
            chapters=[
                Chapter(
                    title="第一章 开始", 
                    content="这是一本中文小说的开头。主人公叫做张三，他住在北京的一个小胡同里。每天早上，张三都会到附近的公园里跑步。今天也不例外。"
                ),
                Chapter(
                    title="第二章 发现",
                    content="在公园里，张三发现了一个奇怪的现象。所有的树叶都变成了金色，就像童话故事中描述的那样神奇。他停下脚步，仔细观察着这个美丽的景象。"
                )
            ]
        )
    ]
    
    # Analyze converted content
    converted_stats = validator.analyze_converted_content(volumes)
    
    # Compare and generate report
    is_valid, result = validator.compare_content()
    report = validator.generate_validation_report()
    
    print(f"Validation result: {'PASSED' if is_valid else 'FAILED'}")
    print("\nGenerated Report Preview:")
    print(report[:500] + "..." if len(report) > 500 else report)
    print("\n" + "="*60 + "\n")

def test_english_book():
    """Test with English content"""
    print("=== Testing English Book ===")
    
    # Sample English text
    english_content = """
    Chapter 1: The Beginning
    
    This is the start of an English novel. The protagonist is named John Smith, 
    and he lives in a small apartment in New York City. Every morning, John goes 
    for a run in the nearby Central Park. Today is no different.
    
    Chapter 2: The Discovery
    
    In the park, John discovered something strange. All the leaves had turned golden, 
    just like in fairy tales. He stopped and carefully observed this beautiful scene.
    The morning sunlight filtered through the golden leaves, creating patterns of light and shadow.
    """
    
    validator = WordCountValidator()
    
    # Analyze original content
    original_stats = validator.analyze_original_content(english_content)
    print(f"Detected language: {validator.detected_language}")
    
    # Create mock converted content
    volumes = [
        Volume(
            title="Test Volume",
            chapters=[
                Chapter(
                    title="Chapter 1: The Beginning", 
                    content="This is the start of an English novel. The protagonist is named John Smith, and he lives in a small apartment in New York City. Every morning, John goes for a run in the nearby Central Park. Today is no different."
                ),
                Chapter(
                    title="Chapter 2: The Discovery",
                    content="In the park, John discovered something strange. All the leaves had turned golden, just like in fairy tales. He stopped and carefully observed this beautiful scene. The morning sunlight filtered through the golden leaves, creating patterns of light and shadow."
                )
            ]
        )
    ]
    
    # Analyze converted content
    converted_stats = validator.analyze_converted_content(volumes)
    
    # Compare and generate report
    is_valid, result = validator.compare_content()
    report = validator.generate_validation_report()
    
    print(f"Validation result: {'PASSED' if is_valid else 'FAILED'}")
    print("\nGenerated Report Preview:")
    print(report[:500] + "..." if len(report) > 500 else report)
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_chinese_book()
    test_english_book()