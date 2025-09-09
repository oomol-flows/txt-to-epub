import re
import logging
from typing import Dict, List, Tuple, Any
from .data_structures import Volume, Chapter, Section

# Configure logging
logger = logging.getLogger(__name__)


class WordCountValidator:
    """Word count validator for comparing text quantity before and after conversion"""
    
    def __init__(self):
        self.original_stats = {}
        self.converted_stats = {}
    
    def clean_text_for_counting(self, text: str) -> str:
        """
        Clean text for counting, remove extra whitespace and punctuation
        
        :param text: Original text
        :return: Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace (spaces, tabs, newlines, etc.)
        cleaned = re.sub(r'\s+', '', text)
        
        # Remove common punctuation and special characters (but keep Chinese characters)
        # Only remove obvious separators, keep potentially meaningful punctuation
        cleaned = re.sub(r'[　\u3000]+', '', cleaned)  # Remove Chinese spaces
        
        return cleaned
    
    def count_characters(self, text: str) -> Dict[str, int]:
        """
        Count characters in text
        
        :param text: Text content
        :return: Character statistics dictionary
        """
        cleaned_text = self.clean_text_for_counting(text)
        
        # Count Chinese characters (including Chinese punctuation)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', cleaned_text))
        
        # Count English letters and numbers
        english_chars = len(re.findall(r'[a-zA-Z0-9]', cleaned_text))
        
        # Count punctuation - use Unicode ranges to avoid encoding issues
        chinese_punctuation = len(re.findall(r'[\u3000-\u303f\uff00-\uffef]', cleaned_text))  # Chinese punctuation
        english_punctuation = len(re.findall(r'[.,!?;:()\[\]<>"\'\\-]', cleaned_text))  # English punctuation
        punctuation = chinese_punctuation + english_punctuation
        
        # Total characters (excluding whitespace)
        total_chars = len(cleaned_text)
        
        # Original text total length (including whitespace)
        original_length = len(text) if text else 0
        
        return {
            'chinese_chars': chinese_chars,
            'english_chars': english_chars,
            'punctuation': punctuation,
            'total_chars': total_chars,
            'original_length': original_length
        }
    
    def analyze_original_content(self, content: str) -> Dict[str, int]:
        """
        Analyze text statistics of original txt file
        
        :param content: Original text content
        :return: Statistics result dictionary
        """
        stats = self.count_characters(content)
        self.original_stats = stats
        
        logger.info(f"Original file statistics:")
        logger.info(f"  - Chinese characters: {stats['chinese_chars']}")
        logger.info(f"  - English characters: {stats['english_chars']}")
        logger.info(f"  - Punctuation: {stats['punctuation']}")
        logger.info(f"  - Total characters (no whitespace): {stats['total_chars']}")
        logger.info(f"  - Original length (with whitespace): {stats['original_length']}")
        
        return stats
    
    def extract_content_from_volumes(self, volumes: List[Volume]) -> str:
        """
        Extract all text content from converted volume structure
        
        :param volumes: Volume list
        :return: Extracted all text content
        """
        all_content = []
        
        for volume in volumes:
            # 添加卷标题（如果有）
            if volume.title:
                all_content.append(volume.title)
            
            for chapter in volume.chapters:
                # 添加章节标题
                if chapter.title:
                    all_content.append(chapter.title)
                
                # 添加章节内容
                if chapter.content:
                    all_content.append(chapter.content)
                
                # 添加节的内容
                for section in chapter.sections:
                    if section.title:
                        all_content.append(section.title)
                    if section.content:
                        all_content.append(section.content)
        
        return '\n'.join(all_content)
    
    def analyze_converted_content(self, volumes: List[Volume]) -> Dict[str, int]:
        """
        分析转换后epub内容的文字统计
        
        :param volumes: 转换后的卷结构
        :return: 统计结果字典
        """
        extracted_content = self.extract_content_from_volumes(volumes)
        stats = self.count_characters(extracted_content)
        self.converted_stats = stats
        
        logger.info(f"转换后内容统计:")
        logger.info(f"  - Chinese characters: {stats['chinese_chars']}")
        logger.info(f"  - English characters: {stats['english_chars']}")
        logger.info(f"  - Punctuation: {stats['punctuation']}")
        logger.info(f"  - Total characters (no whitespace): {stats['total_chars']}")
        logger.info(f"  - Original length (with whitespace): {stats['original_length']}")
        
        return stats
    
    def analyze_content_changes(self) -> Dict[str, str]:
        """
        分析内容变化的原因，提供详细的解释
        
        :return: 包含变化原因分析的字典
        """
        if not self.original_stats or not self.converted_stats:
            return {"error": "缺少统计数据"}
        
        analysis = {}
        diffs = {
            'chinese_chars': self.converted_stats['chinese_chars'] - self.original_stats['chinese_chars'],
            'english_chars': self.converted_stats['english_chars'] - self.original_stats['english_chars'],
            'punctuation': self.converted_stats['punctuation'] - self.original_stats['punctuation'],
            'total_chars': self.converted_stats['total_chars'] - self.original_stats['total_chars']
        }
        
        # 分析中文字符变化
        if abs(diffs['chinese_chars']) <= self.original_stats['chinese_chars'] * 0.005:  # 0.5%以内
            analysis['chinese_reason'] = "中文字符数量基本保持一致，这是正常的。"
            analysis['chinese_concern'] = "无需担心"
        elif diffs['chinese_chars'] > 0:
            analysis['chinese_reason'] = "中文字符数量轻微增加，可能原因：1) 解析器自动添加了章节标题；2) 补充了缺失的标点符号；3) 格式化过程中的正常处理。"
            analysis['chinese_concern'] = "无需担心，这通常是正常的处理结果"
        elif diffs['chinese_chars'] < 0:
            loss_rate = abs(diffs['chinese_chars']) / self.original_stats['chinese_chars'] * 100
            if loss_rate <= 1.0:
                analysis['chinese_reason'] = "中文字符数量轻微减少，可能原因：1) 移除了重复的空白字符；2) 统一了标点符号格式；3) 清理了无效字符。"
                analysis['chinese_concern'] = "基本无需担心，丢失率在可接受范围内"
            else:
                analysis['chinese_reason'] = "中文字符数量明显减少，可能原因：1) 文件编码问题导致部分字符丢失；2) 解析过程中跳过了某些内容；3) 格式识别错误。"
                analysis['chinese_concern'] = "需要关注，建议检查原文件编码和内容结构"
        
        # 分析英文字符变化
        if abs(diffs['english_chars']) <= max(self.original_stats['english_chars'] * 0.02, 10):  # 2%或10个字符以内
            analysis['english_reason'] = "英文字符数量变化很小，这是正常的。可能是格式化时空格处理的差异。"
            analysis['english_concern'] = "无需担心"
        elif diffs['english_chars'] > 0:
            analysis['english_reason'] = "英文字符数量增加，可能原因：1) 解析器添加了HTML标签中的英文；2) 自动生成的章节导航；3) 格式化标识符。"
            analysis['english_concern'] = "无需担心，这通常是EPUB格式的正常需求"
        else:
            loss_rate = abs(diffs['english_chars']) / max(self.original_stats['english_chars'], 1) * 100
            if loss_rate <= 5.0:
                analysis['english_reason'] = "英文字符数量减少，可能原因：1) 移除了多余的空格和换行符；2) 统一了字符编码；3) 清理了格式控制符。"
                analysis['english_concern'] = "基本无需担心"
            else:
                analysis['english_reason'] = "英文字符数量明显减少，可能原因：1) 编码转换问题；2) 解析时遗漏了英文内容；3) 文件结构识别错误。"
                analysis['english_concern'] = "需要关注，建议检查英文内容是否完整"
        
        # 分析标点符号变化
        if abs(diffs['punctuation']) <= max(self.original_stats['punctuation'] * 0.1, 5):  # 10%或5个以内
            analysis['punctuation_reason'] = "标点符号数量变化很小，这是正常的。"
            analysis['punctuation_concern'] = "无需担心"
        elif diffs['punctuation'] > 0:
            analysis['punctuation_reason'] = "标点符号数量增加，可能原因：1) 统一标点符号格式（如半角转全角）；2) 添加了EPUB格式需要的标点；3) 补充了语法标点。"
            analysis['punctuation_concern'] = "无需担心，这有助于阅读体验"
        else:
            analysis['punctuation_reason'] = "标点符号数量减少，可能原因：1) 移除了重复或无意义的标点；2) 统一了标点符号格式；3) 清理了格式控制符。"
            analysis['punctuation_concern'] = "通常无需担心，除非发现阅读时标点明显缺失"
        
        # 分析总体变化
        total_loss_rate = (self.original_stats['total_chars'] - self.converted_stats['total_chars']) / self.original_stats['total_chars'] * 100
        if total_loss_rate <= 0.5:
            analysis['overall_reason'] = "总体字符数量保持稳定，转换质量良好。"
            analysis['overall_concern'] = "内容完整性优秀，可以放心使用"
        elif total_loss_rate <= 1.0:
            analysis['overall_reason'] = "总体字符数量略有减少，主要是格式清理和标准化的结果。"
            analysis['overall_concern'] = "内容完整性良好，正常的处理结果"
        elif total_loss_rate <= 2.0:
            analysis['overall_reason'] = "总体字符数量有所减少，可能是移除了冗余的格式字符和空白。"
            analysis['overall_concern'] = "需要适度关注，建议抽查重要章节内容"
        else:
            analysis['overall_reason'] = "总体字符数量明显减少，可能存在内容解析或转换问题。"
            analysis['overall_concern'] = "需要重点关注，强烈建议检查转换结果"
        
        return analysis
    
    def compare_content(self) -> Tuple[bool, Dict[str, Any]]:
        """
        对比原始内容和转换后内容的差异
        
        :return: (是否通过验证, 对比结果详情)
        """
        if not self.original_stats or not self.converted_stats:
            return False, {"error": "缺少统计数据，请先分析原始内容和转换后内容"}
        
        # 计算差异
        chinese_diff = self.converted_stats['chinese_chars'] - self.original_stats['chinese_chars']
        english_diff = self.converted_stats['english_chars'] - self.original_stats['english_chars']
        punctuation_diff = self.converted_stats['punctuation'] - self.original_stats['punctuation']
        total_diff = self.converted_stats['total_chars'] - self.original_stats['total_chars']
        
        # 计算丢失率
        def calc_loss_rate(original, converted):
            if original == 0:
                return 0.0
            return (original - converted) / original * 100
        
        chinese_loss_rate = calc_loss_rate(self.original_stats['chinese_chars'], self.converted_stats['chinese_chars'])
        english_loss_rate = calc_loss_rate(self.original_stats['english_chars'], self.converted_stats['english_chars'])
        total_loss_rate = calc_loss_rate(self.original_stats['total_chars'], self.converted_stats['total_chars'])
        
        # 验证标准：允许少量字符差异（考虑到解析和格式化的影响）
        # 中文字符丢失率不超过1%，英文字符丢失率不超过2%，总体丢失率不超过1%
        is_valid = (
            chinese_loss_rate <= 1.0 and 
            english_loss_rate <= 2.0 and 
            total_loss_rate <= 1.0 and
            chinese_diff >= -self.original_stats['chinese_chars'] * 0.01  # 中文字符丢失不超过1%
        )
        
        result = {
            "is_valid": is_valid,
            "original_stats": self.original_stats.copy(),
            "converted_stats": self.converted_stats.copy(),
            "differences": {
                "chinese_chars": chinese_diff,
                "english_chars": english_diff,
                "punctuation": punctuation_diff,
                "total_chars": total_diff
            },
            "loss_rates": {
                "chinese_chars": chinese_loss_rate,
                "english_chars": english_loss_rate,
                "total_chars": total_loss_rate
            }
        }
        
        # 记录验证结果
        if is_valid:
            logger.info("✅ 内容验证通过！转换后内容完整性良好")
        else:
            logger.warning("⚠️ 内容验证失败！可能存在内容丢失")
            if chinese_loss_rate > 1.0:
                logger.warning(f"中文字符丢失率过高: {chinese_loss_rate:.2f}%")
            if english_loss_rate > 2.0:
                logger.warning(f"英文字符丢失率过高: {english_loss_rate:.2f}%")
            if total_loss_rate > 1.0:
                logger.warning(f"总体字符丢失率过高: {total_loss_rate:.2f}%")
        
        logger.info(f"字符差异详情:")
        logger.info(f"  - 中文字符差异: {chinese_diff} (丢失率: {chinese_loss_rate:.2f}%)")
        logger.info(f"  - 英文字符差异: {english_diff} (丢失率: {english_loss_rate:.2f}%)")
        logger.info(f"  - 标点符号差异: {punctuation_diff}")
        logger.info(f"  - 总字符差异: {total_diff} (丢失率: {total_loss_rate:.2f}%)")
        
        return is_valid, result
        """
        对比原始内容和转换后内容的差异
        
        :return: (是否通过验证, 对比结果详情)
        """
        if not self.original_stats or not self.converted_stats:
            return False, {"error": "缺少统计数据，请先分析原始内容和转换后内容"}
        
        # 计算差异
        chinese_diff = self.converted_stats['chinese_chars'] - self.original_stats['chinese_chars']
        english_diff = self.converted_stats['english_chars'] - self.original_stats['english_chars']
        punctuation_diff = self.converted_stats['punctuation'] - self.original_stats['punctuation']
        total_diff = self.converted_stats['total_chars'] - self.original_stats['total_chars']
        
        # 计算丢失率
        def calc_loss_rate(original, converted):
            if original == 0:
                return 0.0
            return (original - converted) / original * 100
        
        chinese_loss_rate = calc_loss_rate(self.original_stats['chinese_chars'], self.converted_stats['chinese_chars'])
        english_loss_rate = calc_loss_rate(self.original_stats['english_chars'], self.converted_stats['english_chars'])
        total_loss_rate = calc_loss_rate(self.original_stats['total_chars'], self.converted_stats['total_chars'])
        
        # 验证标准：允许少量字符差异（考虑到解析和格式化的影响）
        # 中文字符丢失率不超过1%，英文字符丢失率不超过2%，总体丢失率不超过1%
        is_valid = (
            chinese_loss_rate <= 1.0 and 
            english_loss_rate <= 2.0 and 
            total_loss_rate <= 1.0 and
            chinese_diff >= -self.original_stats['chinese_chars'] * 0.01  # 中文字符丢失不超过1%
        )
        
        result = {
            "is_valid": is_valid,
            "original_stats": self.original_stats.copy(),
            "converted_stats": self.converted_stats.copy(),
            "differences": {
                "chinese_chars": chinese_diff,
                "english_chars": english_diff,
                "punctuation": punctuation_diff,
                "total_chars": total_diff
            },
            "loss_rates": {
                "chinese_chars": chinese_loss_rate,
                "english_chars": english_loss_rate,
                "total_chars": total_loss_rate
            }
        }
        
        # 记录验证结果
        if is_valid:
            logger.info("✅ 内容验证通过！转换后内容完整性良好")
        else:
            logger.warning("⚠️ 内容验证失败！可能存在内容丢失")
            if chinese_loss_rate > 1.0:
                logger.warning(f"中文字符丢失率过高: {chinese_loss_rate:.2f}%")
            if english_loss_rate > 2.0:
                logger.warning(f"英文字符丢失率过高: {english_loss_rate:.2f}%")
            if total_loss_rate > 1.0:
                logger.warning(f"总体字符丢失率过高: {total_loss_rate:.2f}%")
        
        logger.info(f"字符差异详情:")
        logger.info(f"  - 中文字符差异: {chinese_diff} (丢失率: {chinese_loss_rate:.2f}%)")
        logger.info(f"  - 英文字符差异: {english_diff} (丢失率: {english_loss_rate:.2f}%)")
        logger.info(f"  - 标点符号差异: {punctuation_diff}")
        logger.info(f"  - 总字符差异: {total_diff} (丢失率: {total_loss_rate:.2f}%)")
        
        return is_valid, result
    
    def generate_validation_report(self) -> str:
        """
        生成详细的验证报告（Markdown格式）
        
        :return: Markdown格式的验证报告文本
        """
        is_valid, result = self.compare_content()
        analysis = self.analyze_content_changes()
        
        report = []
        report.append("# TXT转EPUB文字内容完整性验证报告")
        report.append("")
        
        # 使用表格展示转换前后对比
        report.append("## � 转换前后对比")
        report.append("")
        report.append("| 项目 | 转换前 | 转换后 | 差异 | 丢失率 |")
        report.append("|------|--------|--------|------|--------|")
        
        diffs = result['differences']
        rates = result['loss_rates']
        
        def format_diff(diff):
            if diff > 0:
                return f"+{diff:,}"
            elif diff < 0:
                return f"{diff:,}"
            else:
                return "0"
        
        def format_loss_rate(rate):
            if rate > 0:
                return f"{rate:.2f}%"
            else:
                return "0%"
        
        # 添加表格行
        report.append(f"| 中文字符 | {result['original_stats']['chinese_chars']:,} | {result['converted_stats']['chinese_chars']:,} | {format_diff(diffs['chinese_chars'])} | {format_loss_rate(rates['chinese_chars'])} |")
        report.append(f"| 英文字符 | {result['original_stats']['english_chars']:,} | {result['converted_stats']['english_chars']:,} | {format_diff(diffs['english_chars'])} | {format_loss_rate(rates['english_chars'])} |")
        report.append(f"| 标点符号 | {result['original_stats']['punctuation']:,} | {result['converted_stats']['punctuation']:,} | {format_diff(diffs['punctuation'])} | - |")
        report.append(f"| **总字符数** | **{result['original_stats']['total_chars']:,}** | **{result['converted_stats']['total_chars']:,}** | **{format_diff(diffs['total_chars'])}** | **{format_loss_rate(rates['total_chars'])}** |")
        report.append("")
        
        # 验证结果
        if is_valid:
            report.append("## ✅ 验证结果：通过")
            report.append("")
            report.append("转换完成后正文内容完整，没有明显的内容丢失。")
            report.append("")
            report.append("> 💡 **说明**: 少量字符数差异是正常的，通常由以下因素造成：")
            report.append("> - 格式化和标准化处理")
            report.append("> - 空白字符的统一处理")
            report.append("> - 章节结构的重新组织")
            report.append("> - EPUB格式的技术要求")
        else:
            report.append("## ❌ 验证结果：失败")
            report.append("")
            report.append("转换过程中可能存在内容丢失，建议检查：")
            report.append("")
            if rates['chinese_chars'] > 1.0:
                report.append("- ⚠️ 中文字符丢失率超过1%，可能存在编码或解析问题")
            if rates['english_chars'] > 2.0:
                report.append("- ⚠️ 英文字符丢失率超过2%，可能存在格式处理问题")
            if rates['total_chars'] > 1.0:
                report.append("- ⚠️ 总体字符丢失率超过1%，建议检查解析逻辑")
            report.append("")
            report.append("### 🔧 建议的检查步骤")
            report.append("")
            report.append("1. 检查原文件是否使用了特殊编码")
            report.append("2. 确认文件结构是否符合解析规则")
            report.append("3. 验证重要章节内容是否完整")
            report.append("4. 检查是否有特殊格式导致解析错误")
        
        report.append("")
        
        # 差异分析详情表格
        report.append("## 🔍 字数变化原因分析")
        report.append("")
        
        if analysis:
            report.append("| 类型 | 变化原因 | 关注程度 |")
            report.append("|------|----------|----------|")
            
            if 'chinese_reason' in analysis:
                report.append(f"| 中文字符 | {analysis['chinese_reason']} | {analysis['chinese_concern']} |")
            
            if 'english_reason' in analysis:
                report.append(f"| 英文字符 | {analysis['english_reason']} | {analysis['english_concern']} |")
            
            if 'punctuation_reason' in analysis:
                report.append(f"| 标点符号 | {analysis['punctuation_reason']} | {analysis['punctuation_concern']} |")
            
            if 'overall_reason' in analysis:
                report.append(f"| **总体评估** | **{analysis['overall_reason']}** | **{analysis['overall_concern']}** |")
        
        report.append("")
        
        return "\n".join(report)


def validate_conversion_integrity(original_content: str, volumes: List[Volume]) -> Tuple[bool, str]:
    """
    验证txt转epub的内容完整性
    
    :param original_content: 原始txt文件内容
    :param volumes: 转换后的卷结构
    :return: (是否通过验证, 验证报告)
    """
    validator = WordCountValidator()
    
    # 分析原始内容
    validator.analyze_original_content(original_content)
    
    # 分析转换后内容
    validator.analyze_converted_content(volumes)
    
    # 生成验证报告
    report = validator.generate_validation_report()
    
    # 获取验证结果
    is_valid, _ = validator.compare_content()
    
    return is_valid, report
