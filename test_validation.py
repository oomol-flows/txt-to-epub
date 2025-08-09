#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TXT转EPUB转换工具的测试脚本
演示文字数量验证功能
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加任务路径到系统路径
task_path = Path(__file__).parent / "tasks" / "txt-to-epub"
sys.path.insert(0, str(task_path))

from core import txt_to_epub


def create_test_txt_file() -> str:
    """创建一个测试用的txt文件"""
    test_content = """第一卷 测试卷

第一章 测试章节

这是一个测试章节的内容。它包含了中文字符、English characters、数字123，以及各种标点符号：，。！？；：""''（）【】《》、等等。

这段文字用于测试txt转epub的转换质量和文字数量统计功能。

第一节 测试小节

这是第一个小节的内容。小节中也包含了丰富的文本内容，用于验证解析和转换的准确性。

第二节 另一个小节

这是第二个小节，包含更多的测试文字。文字数量验证器会统计所有这些内容，确保转换过程中没有丢失。

第二章 另一个章节

这是第二个章节的内容，没有小节划分。这种情况下，章节内容会直接显示，不会进一步细分。

章节内容包含各种类型的文字：
- 中文汉字
- English letters
- 数字和符号 123 @#$%
- 标点符号：.,!?;:()[]<>"'-

第二卷 第二个测试卷

第三章 第二卷的第一章

这是第二卷的内容。卷的概念在小说中比较常见，用于组织大型作品的结构。

这段内容同样会被统计和验证，确保在转换过程中保持完整。

番外 特殊章节

这是一个特殊的章节类型，不按照常规的章节编号。

番外篇 另一个特殊章节

这也是特殊章节，测试解析器对不同标题格式的处理能力。

结语：
这个测试文件包含了多种文本结构，用于全面测试转换功能和内容完整性验证。
"""
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
        f.write(test_content)
        return f.name


def test_txt_to_epub_with_validation():
    """测试txt转epub转换和内容验证功能"""
    print("=" * 60)
    print("TXT转EPUB转换和内容验证测试")
    print("=" * 60)
    
    # 创建测试文件
    print("📝 创建测试文件...")
    txt_file = create_test_txt_file()
    print(f"测试文件路径: {txt_file}")
    
    # 创建输出文件路径
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    epub_file = output_dir / "test_book.epub"
    
    try:
        print(f"\n🔄 开始转换: {txt_file} -> {epub_file}")
        
        # 执行转换
        result = txt_to_epub(
            txt_file=txt_file,
            epub_file=str(epub_file),
            title="测试书籍",
            author="测试作者"
        )
        
        print(f"\n✅ 转换完成!")
        print(f"输出文件: {result['output_file']}")
        print(f"验证通过: {'是' if result['validation_passed'] else '否'}")
        print(f"生成卷数: {result['volumes_count']}")
        print(f"生成章节数: {result['chapters_count']}")
        
        # 如果验证报告很长，可以保存到文件
        report_file = output_dir / "validation_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(result['validation_report'])
        print(f"详细验证报告已保存到: {report_file}")
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
    finally:
        # 清理临时文件
        try:
            os.unlink(txt_file)
            print(f"\n🧹 已清理临时文件: {txt_file}")
        except:
            pass


if __name__ == "__main__":
    test_txt_to_epub_with_validation()
