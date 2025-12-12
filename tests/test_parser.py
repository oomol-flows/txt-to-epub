#!/usr/bin/env python3
"""
Unit tests for parser module
"""
import unittest
import sys
import os

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'tasks/txt-to-epub-core'))

from parser import (
    detect_language,
    parse_hierarchical_content,
    remove_table_of_contents,
    is_valid_chapter_title,
    validate_and_merge_chapters
)
from parser_config import ParserConfig
from data_structures import Chapter, Volume
import re


class TestLanguageDetection(unittest.TestCase):
    """Test language detection functionality"""

    def test_detect_chinese(self):
        """Test Chinese language detection"""
        content = "这是一本中文书籍，包含很多中文字符。"
        self.assertEqual(detect_language(content), 'chinese')

    def test_detect_english(self):
        """Test English language detection"""
        content = "This is an English book with many English characters."
        self.assertEqual(detect_language(content), 'english')

    def test_detect_mixed_favor_chinese(self):
        """Test mixed content favoring Chinese"""
        content = "这是一本书 with some English words 但主要是中文内容。"
        self.assertEqual(detect_language(content), 'chinese')

    def test_detect_empty(self):
        """Test empty content defaults to Chinese"""
        self.assertEqual(detect_language(""), 'chinese')


class TestChapterDetection(unittest.TestCase):
    """Test chapter detection functionality"""

    def setUp(self):
        """Setup test configuration with length validation disabled"""
        self.config = ParserConfig(enable_length_validation=False)

    def test_chinese_simple_chapters(self):
        """Test simple Chinese chapter detection"""
        long_content = "这是内容。" * 100
        content = f"""
第一章 开始
这是第一章的内容。{long_content}

第二章 继续
这是第二章的内容。{long_content}
"""
        volumes = parse_hierarchical_content(content.strip(), self.config)
        self.assertEqual(len(volumes), 1)
        self.assertEqual(len(volumes[0].chapters), 2)
        self.assertEqual(volumes[0].chapters[0].title, "第一章 开始")
        self.assertEqual(volumes[0].chapters[1].title, "第二章 继续")

    def test_english_simple_chapters(self):
        """Test simple English chapter detection"""
        long_content = "This is content. " * 50
        content = f"""
Chapter 1: Beginning
This is the first chapter content. {long_content}

Chapter 2: Continuing
This is the second chapter content. {long_content}
"""
        volumes = parse_hierarchical_content(content.strip(), self.config)
        self.assertEqual(len(volumes), 1)
        self.assertEqual(len(volumes[0].chapters), 2)
        self.assertIn("Chapter 1", volumes[0].chapters[0].title)
        self.assertIn("Chapter 2", volumes[0].chapters[1].title)

    def test_ignore_inline_chapter_reference(self):
        """Test ignoring inline chapter references"""
        content = """
第一章 开始
在第二章中我们会讨论这个问题。更多内容在第三章。
这是很长的内容，足够长以确保章节验证通过。
""" + "更多内容。" * 100

        volumes = parse_hierarchical_content(content.strip(), self.config)
        # Should only detect 1 chapter, not 3
        self.assertEqual(len(volumes[0].chapters), 1)
        self.assertEqual(volumes[0].chapters[0].title, "第一章 开始")

    def test_chinese_numeric_chapters(self):
        """Test Chinese chapters with Arabic numerals"""
        long_content = "内容" * 100
        content = f"""
第1章 第一章
内容1{long_content}

第2章 第二章
内容2{long_content}
"""
        volumes = parse_hierarchical_content(content.strip(), self.config)
        self.assertEqual(len(volumes[0].chapters), 2)

    def test_special_chapters(self):
        """Test special chapter keywords"""
        long_content = "内容" * 100
        content = f"""
序章 起始
序章内容{long_content}

番外 额外故事
番外内容{long_content}

后记 结束语
后记内容{long_content}
"""
        volumes = parse_hierarchical_content(content.strip(), self.config)
        self.assertGreaterEqual(len(volumes[0].chapters), 3)


class TestChapterValidation(unittest.TestCase):
    """Test chapter title validation"""

    def test_valid_chapter_at_line_start(self):
        """Test valid chapter title at line start"""
        content = """
前言内容

第一章 标题
章节内容
"""
        # Import pattern here to avoid module loading issues
        import re
        pattern = re.compile(r'(?:^|\n)(\s*(?:第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s+[^\n]+|(?:番外|番外篇|外传|特别篇|插话|后记|尾声|终章|楔子|序章)\s+[^\n]*)\s*)(?=\n|$)', re.MULTILINE)
        matches = list(pattern.finditer(content))

        self.assertTrue(len(matches) > 0)
        self.assertTrue(is_valid_chapter_title(matches[0], content, 'chinese'))

    def test_invalid_inline_reference(self):
        """Test invalid inline chapter reference"""
        content = "如前所述，在第一章中我们讨论了这个问题。"
        # Import pattern here
        import re
        pattern = re.compile(r'(?:^|\n)(\s*(?:第([一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬]+|\d{1,3})章\s+[^\n]+|(?:番外|番外篇|外传|特别篇|插话|后记|尾声|终章|楔子|序章)\s+[^\n]*)\s*)(?=\n|$)', re.MULTILINE)
        matches = list(pattern.finditer(content))

        if matches:
            # Should be rejected as inline reference
            self.assertFalse(is_valid_chapter_title(matches[0], content, 'chinese'))


class TestTOCRemoval(unittest.TestCase):
    """Test table of contents removal"""

    def test_remove_chinese_toc(self):
        """Test removing Chinese table of contents"""
        long_content = "这是正文内容。" * 100
        content = f"""
目录
第一章 ....... 1
第二章 ....... 20

第一章 正文开始
{long_content}
"""
        cleaned = remove_table_of_contents(content, 'chinese')
        # TOC should be removed
        self.assertNotIn("....... 1", cleaned)
        self.assertIn("这是正文内容", cleaned)

    def test_remove_english_toc(self):
        """Test removing English table of contents"""
        content = """
Contents
Chapter 1 ....... 1
Chapter 2 ....... 20

Chapter 1: The Beginning
This is the actual content.
"""
        cleaned = remove_table_of_contents(content, 'english')
        self.assertNotIn("....... 1", cleaned)
        self.assertIn("actual content", cleaned)


class TestChapterMerging(unittest.TestCase):
    """Test chapter merging functionality"""

    def test_merge_short_chapters(self):
        """Test merging of short chapters"""
        short_chapter1 = Chapter(title="短章1", content="很短", sections=[])
        short_chapter2 = Chapter(title="短章2", content="也很短", sections=[])
        long_chapter = Chapter(title="长章", content="a" * 1000, sections=[])

        chapters = [short_chapter1, short_chapter2, long_chapter]
        merged = validate_and_merge_chapters(chapters, 'chinese', min_length=500)

        # Short chapters should be merged, resulting in fewer chapters
        self.assertLess(len(merged), len(chapters))

    def test_keep_long_chapters(self):
        """Test that long chapters are kept"""
        long_chapter1 = Chapter(title="章1", content="a" * 1000, sections=[])
        long_chapter2 = Chapter(title="章2", content="b" * 1000, sections=[])

        chapters = [long_chapter1, long_chapter2]
        merged = validate_and_merge_chapters(chapters, 'chinese', min_length=500)

        # Long chapters should not be merged
        self.assertEqual(len(merged), len(chapters))


class TestParserConfig(unittest.TestCase):
    """Test parser configuration"""

    def test_default_config(self):
        """Test default configuration"""
        config = ParserConfig()
        self.assertEqual(config.min_chapter_length, 500)
        self.assertTrue(config.enable_chapter_validation)

    def test_custom_config(self):
        """Test custom configuration"""
        config = ParserConfig(
            min_chapter_length=1000,
            enable_chapter_validation=False
        )
        self.assertEqual(config.min_chapter_length, 1000)
        self.assertFalse(config.enable_chapter_validation)

    def test_config_from_dict(self):
        """Test configuration from dictionary"""
        config_dict = {
            'min_chapter_length': 800,
            'enable_length_validation': False
        }
        config = ParserConfig.from_dict(config_dict)
        self.assertEqual(config.min_chapter_length, 800)
        self.assertFalse(config.enable_length_validation)

    def test_config_with_validation_disabled(self):
        """Test parsing with validation disabled"""
        config = ParserConfig(
            enable_chapter_validation=False,
            enable_length_validation=False
        )

        content = """
第一章 测试
在第二章中会详细说明。
""" + "内容" * 100

        volumes = parse_hierarchical_content(content, config)
        # With validation disabled, might detect inline references
        self.assertGreaterEqual(len(volumes), 1)


class TestVolumeDetection(unittest.TestCase):
    """Test volume/part detection"""

    def test_chinese_volumes(self):
        """Test Chinese volume detection"""
        long_content = "内容" * 100
        content = f"""
第一卷 开始篇

第一章 第一卷第一章
内容1{long_content}

第二卷 继续篇

第二章 第二卷第一章
内容2{long_content}
"""
        volumes = parse_hierarchical_content(content.strip())
        self.assertGreaterEqual(len(volumes), 2)
        self.assertIsNotNone(volumes[0].title)
        self.assertIn("第一卷", volumes[0].title)

    def test_english_parts(self):
        """Test English part detection"""
        long_content = "Content " * 100
        content = f"""
Part I: The Beginning

Chapter 1: Start
Content 1{long_content}

Part II: The Continuation

Chapter 2: Continue
Content 2{long_content}
"""
        volumes = parse_hierarchical_content(content.strip())
        self.assertGreaterEqual(len(volumes), 2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases"""

    def test_empty_content(self):
        """Test empty content handling"""
        volumes = parse_hierarchical_content("")
        self.assertEqual(len(volumes), 1)
        self.assertEqual(volumes[0].chapters[0].title, "Empty Content")

    def test_no_chapters(self):
        """Test content without chapters"""
        content = "这是一段没有章节标记的纯文本内容。" * 100
        volumes = parse_hierarchical_content(content)
        self.assertEqual(len(volumes), 1)
        self.assertEqual(len(volumes[0].chapters), 1)

    def test_very_long_title(self):
        """Test very long chapter title"""
        content = f"""
第一章 {"很长的标题" * 50}
正文内容
"""
        volumes = parse_hierarchical_content(content.strip())
        # Very long titles might be rejected
        # Just ensure it doesn't crash
        self.assertGreaterEqual(len(volumes), 1)

    def test_unicode_content(self):
        """Test Unicode content handling"""
        content = """
第一章 测试🎉
内容包含emoji和特殊字符：©️®️™️
"""
        volumes = parse_hierarchical_content(content.strip())
        self.assertGreaterEqual(len(volumes), 1)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
