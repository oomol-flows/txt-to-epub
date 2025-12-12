# TXT转EPUB大模型智能化设计方案

## 📖 目录

- [概述](#概述)
- [架构设计](#架构设计)
- [核心组件](#核心组件)
- [实施指南](#实施指南)
- [成本优化](#成本优化)
- [使用示例](#使用示例)
- [性能指标](#性能指标)
- [实施路线图](#实施路线图)

---

## 概述

### 设计目标

将大语言模型(LLM)集成到现有的TXT到EPUB转换系统中,解决以下问题:

1. **提升准确率**: 从82%提升到95%+
2. **处理特殊格式**: 支持非标准章节标记
3. **智能消歧**: 区分章节标题与正文引用
4. **自适应能力**: 适应各种书籍格式

### 核心理念

**混合策略**: 规则优先 + LLM辅助

- ✅ 规则处理90%标准情况(快速、免费)
- ✅ LLM处理10%困难情况(准确、智能)
- ✅ 成本控制: ~$0.01-0.05/本书

---

## 架构设计

### 整体流程

```
┌─────────────────────────────────────────────────────────┐
│                    输入: TXT文本                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│           第一阶段: 传统规则解析 (快速)                  │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │ • 正则表达式匹配                          │          │
│  │ • 章节边界识别                            │          │
│  │ • 置信度评分 (0.0-1.0)                   │          │
│  │ • 标记低置信度区域                        │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
│  输出: {                                                │
│    chapters: [...],                                     │
│    uncertain_regions: [低置信度章节],                   │
│    confidence: 0.85                                     │
│  }                                                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
           ┌─────┴─────┐
           │ 置信度检查 │
           └─────┬─────┘
                 │
        ┌────────┴────────┐
        │                 │
     高置信            低置信
    (>0.7)           (<0.7)
        │                 │
        │                 ▼
        │    ┌─────────────────────────────────────┐
        │    │   第二阶段: LLM辅助决策 (智能)       │
        │    │                                      │
        │    │  ┌────────────────────────────┐    │
        │    │  │ • 上下文理解                │    │
        │    │  │ • 语义分析                  │    │
        │    │  │ • 章节边界判断              │    │
        │    │  │ • 消歧处理                  │    │
        │    │  └────────────────────────────┘    │
        │    │                                      │
        │    │  使用技术:                          │
        │    │  - Prompt Caching (降低成本)        │
        │    │  - 批量处理                         │
        │    │  - 结构化输出 (JSON)                │
        │    └─────────────┬───────────────────────┘
        │                  │
        └────────┬─────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│           第三阶段: 结果融合与优化                        │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │ • 合并规则和LLM结果                       │          │
│  │ • 一致性检查                              │          │
│  │ • 冲突解决                                │          │
│  │ • 最终验证                                │          │
│  └──────────────────────────────────────────┘          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                  输出: 结构化章节                        │
│  {                                                       │
│    volumes: [...],                                      │
│    quality_score: 0.95,                                 │
│    llm_calls: 3                                         │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
```

### 决策流程图

```
开始解析
    │
    ▼
规则匹配
    │
    ├──► 匹配成功 ──► 计算置信度
    │                    │
    │                    ├──► 高置信度(>0.7) ──► 接受
    │                    │
    │                    └──► 低置信度(<0.7) ──┐
    │                                          │
    └──► 匹配失败/模糊 ────────────────────────┤
                                              │
                                              ▼
                                        需要LLM介入
                                              │
                                              ▼
                                      LLM分析上下文
                                              │
                                              ├──► 确认为章节 ──► 接受
                                              │
                                              └──► 拒绝/修正 ──► 过滤/修正
                                                      │
                                                      ▼
                                                  最终输出
```

---

## 核心组件

### 1. 置信度评分系统

#### 评分模型

```python
class ConfidenceScorer:
    """章节置信度评分器"""

    def score_chapter(self, match, content, context):
        """
        综合评分,返回0-1之间的置信度

        评分维度:
        1. 模式匹配强度 (40%)
        2. 上下文一致性 (30%)
        3. 章节长度合理性 (20%)
        4. 与其他章节的一致性 (10%)
        """
        score = 1.0

        # 因素1: 模式匹配强度 (40%)
        pattern_score = self._pattern_strength(match)
        score *= (0.4 + 0.6 * pattern_score)

        # 因素2: 上下文一致性 (30%)
        context_score = self._context_consistency(match, content)
        score *= (0.3 + 0.7 * context_score)

        # 因素3: 章节长度合理性 (20%)
        length_score = self._length_reasonableness(match, content)
        score *= (0.2 + 0.8 * length_score)

        # 因素4: 与其他章节的一致性 (10%)
        consistency_score = self._cross_chapter_consistency(match, context)
        score *= (0.1 + 0.9 * consistency_score)

        return score
```

#### 评分细则

| 评分因素 | 高分条件 | 低分条件 |
|---------|---------|---------|
| **模式匹配强度** | "第一章 标题" (1.0) | 模糊匹配 (0.5) |
| **上下文一致性** | 独占一行+前后空行 (1.0) | 句子中间 (0.2) |
| **章节长度** | 500-50000字符 (1.0) | <100或>100000 (0.3) |
| **章节一致性** | 与前后章节风格一致 (1.0) | 格式差异大 (0.4) |

#### LLM介入阈值

```python
def needs_llm_review(self, chapter_info):
    """判断是否需要LLM介入"""
    return (
        chapter_info.confidence < 0.7 or              # 置信度低
        chapter_info.is_ambiguous or                  # 存在歧义
        chapter_info.conflicts_with_neighbors or      # 与邻近章节冲突
        chapter_info.unusual_pattern or               # 非标准格式
        chapter_info.inline_reference_suspected       # 疑似内联引用
    )
```

---

### 2. LLM辅助模块

#### 数据结构

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ChapterCandidate:
    """候选章节"""
    text: str                    # 章节标题文本
    position: int                # 在文档中的位置
    line_number: int            # 行号
    confidence: float           # 规则评分的置信度
    context_before: str         # 前文上下文
    context_after: str          # 后文上下文
    pattern_type: str           # 匹配模式类型
    issues: List[str]           # 存在的问题列表


@dataclass
class LLMDecision:
    """LLM决策结果"""
    is_chapter: bool            # 是否为真实章节
    confidence: float           # LLM的置信度
    reason: str                 # 判断理由
    suggested_title: Optional[str] = None  # 建议的标题(如需修正)
    suggested_position: Optional[int] = None  # 建议的位置
```

#### Prompt模板设计

##### 场景1: 章节边界判断

```python
CHAPTER_BOUNDARY_PROMPT = """
你是一个专业的文档结构分析专家。请判断以下文本片段中哪些是真正的章节标题。

【文档信息】
- 文档类型: {doc_type}
- 语言: {language}
- 已识别章节数: {existing_chapter_count}
- 平均章节长度: {avg_chapter_length}字

【已确认章节示例】
{existing_chapters_sample}

【待分析文本】
{text_snippet}

【候选章节】
{candidates_list}

请仔细分析每个候选项的上下文,判断其是否为真正的章节标题,还是:
- 正文中的章节引用 (如"在第三章中讨论过")
- 目录条目
- 其他非章节标记

输出JSON格式:
{{
  "decisions": [
    {{
      "candidate": "第一章 标题",
      "is_chapter": true,
      "confidence": 0.95,
      "reason": "独占一行,格式标准,后跟正文内容,与已识别章节风格一致",
      "position": "keep"
    }},
    {{
      "candidate": "在第二章中",
      "is_chapter": false,
      "confidence": 0.92,
      "reason": "位于句子中间,前有'在'字,后有'中'字,明显是引用",
      "position": "reject"
    }}
  ],
  "overall_analysis": "共识别2个候选项,1个有效章节,1个内联引用"
}}

注意事项:
1. 重点关注候选项在文本中的位置和上下文
2. 考虑与已有章节的一致性
3. 识别常见的引用模式
4. 给出明确的判断理由
"""
```

##### 场景2: 模糊章节消歧

```python
DISAMBIGUATION_PROMPT = """
以下文本存在歧义,需要你的专业判断。

【问题描述】
在以下文本中,"{ambiguous_text}"可能是:
A) 章节标题
B) 正文中的词语/引用

【文本片段】
{text_context}

【背景信息】
- 前一章节: {prev_chapter}
- 前一章节长度: {prev_chapter_length}字
- 文档风格: {doc_style}
- 语言: {language}

【分析要点】
1. 该文本是否独占一行?
2. 前后是否有空行分隔?
3. 是否在句子的语法结构中?
4. 格式是否符合其他章节标题?
5. 如果是章节,长度是否合理?

请给出你的分析:
{{
  "decision": "chapter" 或 "reference" 或 "unclear",
  "confidence": 0.0-1.0,
  "analysis": {{
    "line_position": "独占一行/句子中间",
    "surrounding_context": "有空行分隔/紧接上文",
    "format_consistency": "与其他章节一致/格式不符",
    "length_check": "长度合理/过短过长"
  }},
  "recommendation": "具体建议",
  "reason": "详细理由"
}}
"""
```

##### 场景3: 无标记文本结构推断

```python
STRUCTURE_INFERENCE_PROMPT = """
以下文本没有明显的章节标记,请基于内容和语义推断章节结构。

【任务】
分析文本的主题变化,建议合理的章节划分。

【文本样本】(前{sample_length}字)
{content_sample}

【分析维度】
1. 主题转换点: 内容主题发生明显变化的位置
2. 段落结构: 是否存在明显的段落分组
3. 语义连贯性: 哪些段落在语义上紧密相关
4. 自然分界: 是否有明显的分节标记(如"***", "---")

【输出要求】
{{
  "suggested_chapters": [
    {{
      "start_position": 0,
      "end_position": 1523,
      "suggested_title": "引言:研究背景",
      "reason": "介绍研究背景和动机,主题独立完整",
      "confidence": 0.85,
      "key_topics": ["背景", "动机", "研究意义"]
    }},
    {{
      "start_position": 1524,
      "end_position": 3890,
      "suggested_title": "第一部分:理论基础",
      "reason": "转入理论阐述,与前文明显不同",
      "confidence": 0.78,
      "key_topics": ["概念定义", "理论框架"]
    }}
  ],
  "confidence_level": "high/medium/low",
  "notes": "额外说明"
}}

注意:
- 章节数量控制在合理范围(建议5-20章)
- 每章长度尽量均衡
- 标题简洁明确
- 给出清晰的划分依据
"""
```

##### 场景4: 特殊格式识别

```python
SPECIAL_FORMAT_PROMPT = """
这是一本特殊格式的书籍,请帮助识别其章节结构。

【文本样本】
{text_sample}

【观察到的模式】
{observed_patterns}

【问题】
1. 该书采用什么章节标记方式?
2. 如何区分章节标题和正文?
3. 是否有特殊的结构层次?

请分析并提供:
{{
  "format_type": "章回体/诗歌集/剧本/论文/其他",
  "chapter_pattern": "正则表达式或描述",
  "identification_rules": [
    "规则1: ...",
    "规则2: ..."
  ],
  "sample_chapters": [
    {{"title": "...", "position": ...}}
  ],
  "confidence": 0.0-1.0,
  "suggested_regex": "建议的正则表达式"
}}
"""
```

---

### 3. LLM辅助类实现

#### 完整实现代码

```python
"""
LLM-assisted parser for ambiguous chapter detection
大模型辅助解析器 - 用于处理模糊章节识别
"""
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChapterCandidate:
    """候选章节数据结构"""
    text: str
    position: int
    line_number: int
    confidence: float
    context_before: str
    context_after: str
    pattern_type: str
    issues: List[str] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []


@dataclass
class LLMDecision:
    """LLM决策结果数据结构"""
    is_chapter: bool
    confidence: float
    reason: str
    suggested_title: Optional[str] = None
    suggested_position: Optional[int] = None


class LLMParserAssistant:
    """LLM辅助解析器"""

    def __init__(self, llm_client, model="claude-3-5-sonnet-20241022"):
        """
        初始化LLM助手

        :param llm_client: Anthropic client或其他LLM客户端
        :param model: 使用的模型
        """
        self.client = llm_client
        self.model = model
        self.cache_enabled = True
        self.max_tokens = 4096

        # 统计信息
        self.stats = {
            'total_calls': 0,
            'cache_hits': 0,
            'total_tokens': 0,
            'total_cost': 0.0
        }

    def analyze_chapter_candidates(
        self,
        candidates: List[ChapterCandidate],
        full_content: str,
        existing_chapters: List[Dict],
        doc_context: Dict = None
    ) -> List[LLMDecision]:
        """
        分析候选章节,判断是否为真实章节

        :param candidates: 候选章节列表
        :param full_content: 完整文本内容
        :param existing_chapters: 已确认的章节信息
        :param doc_context: 文档上下文信息
        :return: 决策结果列表
        """
        if not candidates:
            return []

        logger.info(f"LLM analyzing {len(candidates)} candidates...")

        # 构建prompt
        prompt = self._build_chapter_analysis_prompt(
            candidates,
            full_content,
            existing_chapters,
            doc_context
        )

        # 调用LLM
        response = self._call_llm(prompt, use_cache=True)

        # 解析响应
        decisions = self._parse_llm_response(response)

        # 更新统计
        confirmed = sum(1 for d in decisions if d.is_chapter)
        logger.info(f"LLM confirmed {confirmed}/{len(candidates)} as chapters")

        return decisions

    def infer_chapter_structure(
        self,
        content: str,
        max_length: int = 10000,
        language: str = 'chinese'
    ) -> List[Dict]:
        """
        对无明显章节标记的文本,推断章节结构

        :param content: 文本内容
        :param max_length: 最大分析长度
        :param language: 文档语言
        :return: 建议的章节结构
        """
        logger.info(f"LLM inferring structure for {len(content)} chars...")

        # 截取分析样本
        sample = content[:max_length]

        prompt = f"""
你是文档结构分析专家。以下文本没有明显章节标记,请分析并建议章节划分。

【文本样本】({len(sample)}字符)
{sample}

【语言】{language}

【任务】
1. 识别内容的主题变化点
2. 建议章节划分位置
3. 为每个章节生成标题

输出JSON格式:
{{
  "suggested_chapters": [
    {{
      "start_char": 0,
      "end_char": 500,
      "title": "建议标题",
      "reason": "划分依据",
      "confidence": 0.85
    }}
  ],
  "format_analysis": "格式特点分析",
  "confidence": 0.8
}}
"""

        response = self._call_llm(prompt, max_tokens=2048)
        result = self._parse_structure_response(response)

        logger.info(f"LLM suggested {len(result)} chapters")
        return result

    def disambiguate_reference(
        self,
        text_snippet: str,
        candidate: str,
        context: Dict
    ) -> Dict:
        """
        消歧:判断是章节标题还是正文引用

        :param text_snippet: 包含候选的文本片段
        :param candidate: 候选章节文本
        :param context: 上下文信息
        :return: 决策字典
        """
        logger.debug(f"LLM disambiguating: {candidate}")

        prompt = f"""
判断以下文本中的"{candidate}"是章节标题还是正文中的引用?

【文本片段】
{text_snippet}

【上下文】
- 前一章节: {context.get('prev_chapter', 'N/A')}
- 文档类型: {context.get('doc_type', '未知')}
- 语言: {context.get('language', '未知')}

分析要点:
1. 位置: 独占一行还是句子中间?
2. 语法: 是否在句子结构中?
3. 格式: 是否符合章节标题格式?

回答格式:
{{
  "type": "chapter" 或 "reference",
  "confidence": 0.0-1.0,
  "reason": "判断理由"
}}
"""

        response = self._call_llm(prompt, max_tokens=256)
        result = json.loads(response)

        logger.debug(f"Decision: {result['type']} (confidence: {result['confidence']})")
        return result

    def identify_special_format(
        self,
        content_sample: str,
        observed_patterns: List[str]
    ) -> Dict:
        """
        识别特殊格式书籍的章节模式

        :param content_sample: 文本样本
        :param observed_patterns: 观察到的模式
        :return: 格式识别结果
        """
        logger.info("LLM identifying special format...")

        patterns_text = "\n".join(f"- {p}" for p in observed_patterns)

        prompt = f"""
这是一本特殊格式的书籍,请帮助识别其章节结构。

【文本样本】
{content_sample[:2000]}

【观察到的模式】
{patterns_text}

请分析:
1. 该书采用什么章节标记方式?
2. 如何识别章节边界?
3. 建议的正则表达式

输出JSON:
{{
  "format_type": "格式类型",
  "chapter_pattern": "模式描述",
  "identification_rules": ["规则1", "规则2"],
  "sample_chapters": [{{"title": "...", "position": 0}}],
  "confidence": 0.8,
  "suggested_regex": "正则表达式"
}}
"""

        response = self._call_llm(prompt, max_tokens=1024)
        result = json.loads(response)

        logger.info(f"Identified format: {result.get('format_type', 'unknown')}")
        return result

    def _build_chapter_analysis_prompt(
        self,
        candidates: List[ChapterCandidate],
        full_content: str,
        existing_chapters: List[Dict],
        doc_context: Dict = None
    ) -> str:
        """构建章节分析prompt"""

        doc_context = doc_context or {}

        # 计算平均章节长度
        if existing_chapters:
            avg_length = sum(ch.get('length', 0) for ch in existing_chapters) / len(existing_chapters)
        else:
            avg_length = 0

        # 格式化候选项
        candidates_text = []
        for i, c in enumerate(candidates, 1):
            issues_text = f" [问题: {', '.join(c.issues)}]" if c.issues else ""
            candidates_text.append(
                f"{i}. \"{c.text}\" (第{c.line_number}行, "
                f"置信度:{c.confidence:.2f}, 类型:{c.pattern_type}){issues_text}"
            )

        # 提取每个候选的上下文
        contexts = []
        for i, c in enumerate(candidates, 1):
            context = f"""
【候选{i}上下文】
前文: ...{c.context_before}
>>> {c.text} <<<
后文: {c.context_after}...
"""
            contexts.append(context)

        # 已确认章节示例
        chapter_examples = []
        for ch in existing_chapters[:5]:
            chapter_examples.append(f"- {ch.get('title', 'Unknown')}")

        prompt = f"""
你是文档结构分析专家。请判断以下候选项是否为真正的章节标题。

【文档信息】
- 文档类型: {doc_context.get('doc_type', '未知')}
- 语言: {doc_context.get('language', '未知')}
- 已识别章节数: {len(existing_chapters)}
- 平均章节长度: {avg_length:.0f}字

【已确认章节示例】
{chr(10).join(chapter_examples) if chapter_examples else '暂无'}

【待判断候选项】
{chr(10).join(candidates_text)}

{chr(10).join(contexts)}

【判断标准】
1. ✓ 独占一行
2. ✓ 前后有适当分隔
3. ✓ 不在句子语法结构中
4. ✓ 格式与已识别章节一致
5. ✗ 位于句子中间
6. ✗ 前有"在/如/见"等引用词
7. ✗ 后有"中/里/结束时"等连接词

请为每个候选给出判断,JSON格式:
{{
  "decisions": [
    {{
      "index": 1,
      "is_chapter": true/false,
      "confidence": 0.0-1.0,
      "reason": "详细理由",
      "action": "accept/reject/modify",
      "suggested_title": "如需修改的标题"
    }}
  ],
  "overall_analysis": "整体分析"
}}
"""
        return prompt

    def _call_llm(
        self,
        prompt: str,
        use_cache: bool = False,
        max_tokens: int = None
    ) -> str:
        """
        调用LLM API

        :param prompt: 提示词
        :param use_cache: 是否使用prompt caching
        :param max_tokens: 最大token数
        :return: LLM响应文本
        """
        try:
            self.stats['total_calls'] += 1

            messages = [{"role": "user", "content": prompt}]

            # Anthropic API调用
            if hasattr(self.client, 'messages'):
                system_message = {
                    "type": "text",
                    "text": "你是专业的文档结构分析助手,擅长识别章节和目录结构。"
                }

                # 启用prompt caching
                if use_cache and self.cache_enabled:
                    system_message["cache_control"] = {"type": "ephemeral"}

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens or self.max_tokens,
                    messages=messages,
                    system=[system_message]
                )

                # 更新统计
                usage = response.usage
                self.stats['total_tokens'] += usage.input_tokens + usage.output_tokens

                # 估算成本 (Claude 3.5 Sonnet价格)
                input_cost = usage.input_tokens * 0.003 / 1000
                output_cost = usage.output_tokens * 0.015 / 1000
                self.stats['total_cost'] += input_cost + output_cost

                return response.content[0].text

            # 其他LLM客户端
            else:
                response = self.client.complete(prompt)
                return response

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    def _parse_llm_response(self, response: str) -> List[LLMDecision]:
        """解析LLM JSON响应"""
        try:
            # 提取JSON (处理markdown代码块)
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()

            data = json.loads(response)
            decisions = []

            for item in data.get('decisions', []):
                decisions.append(LLMDecision(
                    is_chapter=item.get('is_chapter', False),
                    confidence=item.get('confidence', 0.5),
                    reason=item.get('reason', ''),
                    suggested_title=item.get('suggested_title'),
                    suggested_position=item.get('suggested_position')
                ))

            return decisions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"Response was: {response}")
            return []

    def _parse_structure_response(self, response: str) -> List[Dict]:
        """解析结构推断响应"""
        try:
            # 同样处理markdown
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()

            data = json.loads(response)
            return data.get('suggested_chapters', [])

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse structure response: {e}")
            return []

    def get_stats(self) -> Dict:
        """获取使用统计"""
        return self.stats.copy()

    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'total_calls': 0,
            'cache_hits': 0,
            'total_tokens': 0,
            'total_cost': 0.0
        }
```

---

### 4. 混合解析器实现

```python
class HybridParser:
    """混合解析器: 规则 + LLM"""

    def __init__(
        self,
        llm_client=None,
        config: ParserConfig = None
    ):
        """
        初始化混合解析器

        :param llm_client: LLM客户端(可选)
        :param config: 解析器配置
        """
        self.config = config or DEFAULT_CONFIG
        self.rule_parser = RuleBasedParserWithConfidence()
        self.llm_assistant = LLMParserAssistant(llm_client) if llm_client else None

    def parse(self, content: str) -> List[Volume]:
        """
        混合解析流程

        :param content: 文本内容
        :return: 卷列表
        """
        # 阶段1: 规则解析 + 置信度评分
        logger.info("Phase 1: Rule-based parsing...")
        rule_result = self.rule_parser.parse_with_confidence(content)

        # 如果整体置信度高,直接返回
        if rule_result['overall_confidence'] > 0.85:
            logger.info(f"High confidence ({rule_result['overall_confidence']:.2f}), "
                       f"skipping LLM assistance")
            return rule_result['volumes']

        # 阶段2: 识别需要LLM的区域
        uncertain_regions = rule_result.get('uncertain_regions', [])

        if uncertain_regions and self.llm_assistant:
            logger.info(f"Phase 2: LLM assistance for {len(uncertain_regions)} uncertain regions...")

            # 转换为候选格式
            candidates = self._convert_to_candidates(uncertain_regions, content)

            # LLM分析
            llm_decisions = self.llm_assistant.analyze_chapter_candidates(
                candidates,
                content,
                rule_result['chapters'],
                {'language': detect_language(content)}
            )

            # 阶段3: 融合结果
            logger.info("Phase 3: Merging results...")
            final_volumes = self._merge_results(
                rule_result['volumes'],
                llm_decisions,
                candidates
            )

            # 输出统计
            stats = self.llm_assistant.get_stats()
            logger.info(f"LLM Stats: {stats['total_calls']} calls, "
                       f"${stats['total_cost']:.4f} cost")

            return final_volumes

        # 无需LLM或未提供客户端
        return rule_result['volumes']

    def _convert_to_candidates(
        self,
        uncertain_regions: List[Dict],
        content: str
    ) -> List[ChapterCandidate]:
        """转换为候选格式"""
        candidates = []

        for region in uncertain_regions:
            chapter = region['chapter']
            confidence = region['confidence']

            # 查找在内容中的位置
            position = content.find(chapter.title)

            # 提取上下文
            context_size = 200
            context_before = content[max(0, position-context_size):position]
            context_after = content[position+len(chapter.title):position+len(chapter.title)+context_size]

            # 计算行号
            line_number = content[:position].count('\n') + 1

            # 确定问题
            issues = []
            if confidence < 0.5:
                issues.append("极低置信度")
            elif confidence < 0.7:
                issues.append("低置信度")

            if "第" in chapter.title and ("在" in context_before[-10:] or "如" in context_before[-10:]):
                issues.append("疑似引用")

            candidates.append(ChapterCandidate(
                text=chapter.title,
                position=position,
                line_number=line_number,
                confidence=confidence,
                context_before=context_before,
                context_after=context_after,
                pattern_type=region.get('pattern_type', 'standard'),
                issues=issues
            ))

        return candidates

    def _merge_results(
        self,
        rule_volumes: List[Volume],
        llm_decisions: List[LLMDecision],
        candidates: List[ChapterCandidate]
    ) -> List[Volume]:
        """融合规则和LLM结果"""

        # 创建决策映射
        decision_map = {
            candidates[i].text: llm_decisions[i]
            for i in range(len(llm_decisions))
        }

        # 处理每个卷
        new_volumes = []
        for volume in rule_volumes:
            new_chapters = []

            for chapter in volume.chapters:
                decision = decision_map.get(chapter.title)

                if decision:
                    if decision.is_chapter:
                        # LLM确认为章节
                        if decision.suggested_title:
                            # 使用建议的标题
                            new_chapter = Chapter(
                                title=decision.suggested_title,
                                content=chapter.content,
                                sections=chapter.sections
                            )
                            new_chapters.append(new_chapter)
                        else:
                            new_chapters.append(chapter)
                    else:
                        # LLM拒绝,不添加
                        logger.info(f"LLM rejected chapter: {chapter.title}")
                else:
                    # 无LLM决策,保留原结果
                    new_chapters.append(chapter)

            if new_chapters:
                new_volumes.append(Volume(
                    title=volume.title,
                    chapters=new_chapters
                ))

        return new_volumes


class RuleBasedParserWithConfidence:
    """带置信度评分的规则解析器"""

    def parse_with_confidence(self, content: str) -> Dict:
        """
        解析内容并返回置信度

        :return: {
            'volumes': [...],
            'chapters': [...],
            'uncertain_regions': [...],
            'overall_confidence': 0.85
        }
        """
        from .parser import parse_hierarchical_content

        # 使用现有解析器
        volumes = parse_hierarchical_content(content)

        # 为每个章节计算置信度
        chapters_with_confidence = []
        uncertain_regions = []

        for volume in volumes:
            for chapter in volume.chapters:
                # 计算置信度
                confidence = self._estimate_confidence(chapter, content)

                chapter_info = {
                    'chapter': chapter,
                    'confidence': confidence,
                    'volume': volume,
                    'length': len(chapter.content) + sum(len(s.content) for s in chapter.sections)
                }

                chapters_with_confidence.append(chapter_info)

                if confidence < 0.7:
                    uncertain_regions.append(chapter_info)

        if chapters_with_confidence:
            overall_confidence = sum(c['confidence'] for c in chapters_with_confidence) / len(chapters_with_confidence)
        else:
            overall_confidence = 0.0

        return {
            'volumes': volumes,
            'chapters': chapters_with_confidence,
            'uncertain_regions': uncertain_regions,
            'overall_confidence': overall_confidence
        }

    def _estimate_confidence(self, chapter, content: str) -> float:
        """估算章节置信度"""
        score = 0.6  # 基础分

        # 因素1: 标题长度
        title_len = len(chapter.title)
        if 5 <= title_len <= 30:
            score += 0.15
        elif title_len < 5 or title_len > 50:
            score -= 0.1

        # 因素2: 内容长度
        total_length = len(chapter.content) + sum(len(s.content) for s in chapter.sections)
        if 500 <= total_length <= 50000:
            score += 0.15
        elif total_length < 100:
            score -= 0.2

        # 因素3: 标题格式
        if re.match(r'第[一二三四五六七八九十百千万\d]+章', chapter.title):
            score += 0.1  # 标准格式

        # 因素4: 位置检查(简化)
        position = content.find(chapter.title)
        if position > 0:
            before = content[max(0, position-20):position]
            if re.search(r'[在如见]第', before):
                score -= 0.3  # 疑似引用

        return max(0.0, min(1.0, score))
```

---

## 成本优化

### 1. Prompt Caching

使用Anthropic的Prompt Caching功能:

```python
# 系统提示词会被缓存
system_message = {
    "type": "text",
    "text": "你是专业的文档结构分析助手...",  # 这部分会被缓存
    "cache_control": {"type": "ephemeral"}
}

# 首次调用: 正常计费
# 后续调用: 缓存命中, 成本降低90%
```

**节省**: 90%的输入token成本

### 2. 批量处理

```python
def batch_analyze_candidates(self, candidates: List[ChapterCandidate]):
    """一次调用分析多个候选,而非多次调用"""
    # 一次性发送所有候选
    # 而非逐个发送
    pass
```

**节省**: 减少API调用次数

### 3. 智能触发

```python
# 仅当需要时调用LLM
if overall_confidence > 0.85:
    # 跳过LLM,直接使用规则结果
    return rule_result
```

**节省**: 90%的书籍不需要LLM

### 4. 成本估算

| 场景 | LLM调用次数 | 成本估算 |
|------|------------|---------|
| 标准书籍 | 0 | $0.00 |
| 轻度模糊 | 1-3次 | $0.01-0.03 |
| 中度模糊 | 3-5次 | $0.03-0.05 |
| 重度模糊 | 5-10次 | $0.05-0.10 |
| 特殊格式 | 10+次 | $0.10+ |

**平均成本**: ~$0.02/本

---

## 使用示例

### 示例1: 基础集成

```python
from anthropic import Anthropic
from tasks.txt_to_epub_core.parser_config import ParserConfig
from tasks.txt_to_epub_core.llm_parser_assistant import HybridParser

# 初始化
client = Anthropic(api_key="your-api-key")

config = ParserConfig(
    enable_llm_assistance=True,
    llm_confidence_threshold=0.7
)

# 创建混合解析器
parser = HybridParser(llm_client=client, config=config)

# 解析文本
with open('book.txt', 'r') as f:
    content = f.read()

volumes = parser.parse(content)

print(f"解析完成: {len(volumes)} 卷")
for volume in volumes:
    print(f"- {volume.title or '主体'}: {len(volume.chapters)} 章")
```

### 示例2: 特殊格式识别

```python
# 识别特殊格式
assistant = LLMParserAssistant(client)

# 提取样本
sample = content[:2000]
observed_patterns = ["* * *", "---", "Chapter:", "PART"]

# LLM识别格式
format_info = assistant.identify_special_format(sample, observed_patterns)

print(f"格式类型: {format_info['format_type']}")
print(f"建议正则: {format_info['suggested_regex']}")

# 使用识别结果更新配置
config.custom_chapter_patterns.append(format_info['suggested_regex'])
```

### 示例3: 消歧处理

```python
# 处理模糊章节
ambiguous_text = "在第三章中我们讨论了这个问题"

decision = assistant.disambiguate_reference(
    text_snippet=ambiguous_text,
    candidate="第三章",
    context={'prev_chapter': '第二章 背景', 'language': 'chinese'}
)

if decision['type'] == 'reference':
    print(f"这是引用,不是章节: {decision['reason']}")
```

### 示例4: 结构推断

```python
# 对无章节标记的文本
result = assistant.infer_chapter_structure(
    content=content,
    max_length=10000,
    language='chinese'
)

for chapter in result:
    print(f"建议章节: {chapter['title']}")
    print(f"  位置: {chapter['start_char']}-{chapter['end_char']}")
    print(f"  理由: {chapter['reason']}")
    print(f"  置信度: {chapter['confidence']}")
```

### 示例5: 完整转换流程

```python
from tasks.txt_to_epub_core.core import txt_to_epub

# 完整转换(带LLM辅助)
result = txt_to_epub(
    txt_file='novel.txt',
    epub_file='novel.epub',
    title='我的小说',
    author='作者名',
    config=config,  # 启用LLM的配置
    llm_client=client,  # 传入LLM客户端
    show_progress=True
)

# 查看结果
print(f"转换成功: {result['success']}")
print(f"章节数: {result['chapters_count']}")
print(f"验证通过: {result['validation_passed']}")

# 查看LLM统计
if 'llm_stats' in result:
    stats = result['llm_stats']
    print(f"LLM调用: {stats['total_calls']}次")
    print(f"总成本: ${stats['total_cost']:.4f}")
```

---

## 性能指标

### 预期效果对比

| 指标 | 纯规则 | 混合模式(规则+LLM) |
|------|--------|-------------------|
| **准确率** | 82% | **95%+** ⬆️ |
| **标准格式识别** | 95% | 98% ⬆️ |
| **特殊格式识别** | 40% | **85%** ⬆️ |
| **误识别率** | 18% | **3%** ⬇️ |
| **处理速度** | 8s/本 | 9-12s/本 ⬇️ |
| **成本** | $0 | **~$0.02/本** |
| **适应性** | 低 | **高** ⬆️ |

### 各场景表现

| 书籍类型 | 规则准确率 | 混合准确率 | LLM调用 | 成本 |
|---------|-----------|-----------|---------|------|
| 标准网文 | 95% | 98% | 0-1次 | $0-0.01 |
| 学术论文 | 70% | 92% | 2-3次 | $0.02 |
| 特殊格式 | 30% | 88% | 5-8次 | $0.05 |
| 无标记文本 | 10% | 75% | 3-5次 | $0.03 |
| 混合标记 | 60% | 90% | 3-4次 | $0.03 |

### 速度对比

```
┌─────────────────────────────────────────┐
│            处理速度对比                  │
├─────────────────────────────────────────┤
│ 纯规则:     ████████ 8s                 │
│ 混合(高置信): █████████ 9s              │
│ 混合(中置信): ██████████ 10s            │
│ 混合(低置信): ████████████ 12s          │
└─────────────────────────────────────────┘
```

---

## 实施路线图

### Phase 1: 基础框架 (1-2周)

**目标**: 搭建LLM集成基础架构

**任务**:
- [x] 设计置信度评分系统
- [ ] 实现 `ConfidenceScorer` 类
- [ ] 实现 `LLMParserAssistant` 基础类
- [ ] 实现 `HybridParser` 框架
- [ ] 编写基础prompt模板
- [ ] 单元测试(覆盖率>80%)

**交付物**:
- `confidence_scorer.py`
- `llm_parser_assistant.py`
- `hybrid_parser.py`
- 测试用例

### Phase 2: 核心功能 (2-3周)

**目标**: 实现主要功能和优化

**任务**:
- [ ] 实现章节边界判断
- [ ] 实现消歧功能
- [ ] 实现prompt caching
- [ ] 实现批量处理
- [ ] 成本追踪和统计
- [ ] 集成到现有parser.py

**交付物**:
- 完整的LLM辅助功能
- 成本统计dashboard
- 性能测试报告

### Phase 3: 高级特性 (2-3周)

**目标**: 增强能力和用户体验

**任务**:
- [ ] 特殊格式识别
- [ ] 结构推断功能
- [ ] 用户反馈收集
- [ ] A/B测试框架
- [ ] 配置界面

**交付物**:
- 特殊格式支持
- 用户反馈系统
- 配置工具

### Phase 4: 学习系统 (3-4周)

**目标**: 持续改进和自适应

**任务**:
- [ ] 规则自动更新
- [ ] 案例库构建
- [ ] 模式学习
- [ ] 性能监控
- [ ] 自动优化

**交付物**:
- 自学习系统
- 监控dashboard
- 优化报告

---

## 配置说明

### parser_config.py 扩展

```python
@dataclass
class ParserConfig:
    # ... 现有配置 ...

    # ========== LLM辅助配置 ==========

    # 基础开关
    enable_llm_assistance: bool = False
    """是否启用LLM辅助 (默认关闭)"""

    # 触发条件
    llm_confidence_threshold: float = 0.7
    """LLM介入的置信度阈值 (0.0-1.0)"""

    llm_trigger_on_ambiguous: bool = True
    """在模糊情况下自动触发LLM"""

    llm_trigger_on_conflict: bool = True
    """在章节冲突时触发LLM"""

    # 模型配置
    llm_model: str = "claude-3-5-sonnet-20241022"
    """使用的LLM模型"""

    llm_max_tokens: int = 4096
    """LLM响应的最大token数"""

    # 成本控制
    llm_max_calls_per_book: int = 10
    """每本书最多LLM调用次数"""

    llm_max_cost_per_book: float = 0.10
    """每本书最高成本 (USD)"""

    llm_cache_enabled: bool = True
    """启用prompt caching降低成本"""

    # 批处理
    llm_batch_size: int = 5
    """批量处理的候选章节数量"""

    # 策略选择
    llm_strategy: str = "hybrid"
    """
    解析策略:
    - 'rule_only': 仅使用规则
    - 'hybrid': 混合模式(推荐)
    - 'llm_first': LLM优先
    - 'llm_only': 仅使用LLM
    """

    # 功能开关
    llm_enable_disambiguation: bool = True
    """启用消歧功能"""

    llm_enable_structure_inference: bool = False
    """启用结构推断(实验性)"""

    llm_enable_format_detection: bool = True
    """启用特殊格式检测"""

    # 调试
    llm_debug_mode: bool = False
    """LLM调试模式(记录所有prompt和响应)"""

    llm_save_prompts: bool = False
    """保存所有prompt到文件"""
```

### 使用配置示例

```python
# 保守模式: 仅处理极低置信度
conservative_config = ParserConfig(
    enable_llm_assistance=True,
    llm_confidence_threshold=0.5,  # 很低才触发
    llm_max_calls_per_book=3,      # 最多3次
    llm_max_cost_per_book=0.03     # 最多$0.03
)

# 平衡模式: 推荐配置
balanced_config = ParserConfig(
    enable_llm_assistance=True,
    llm_confidence_threshold=0.7,
    llm_max_calls_per_book=10,
    llm_max_cost_per_book=0.10,
    llm_cache_enabled=True
)

# 激进模式: 最大化准确率
aggressive_config = ParserConfig(
    enable_llm_assistance=True,
    llm_confidence_threshold=0.85,  # 高阈值
    llm_max_calls_per_book=20,
    llm_enable_structure_inference=True,
    llm_enable_format_detection=True
)
```

---

## 监控和调试

### 统计信息

```python
# 获取LLM使用统计
stats = assistant.get_stats()

print(f"""
LLM使用统计:
- 总调用次数: {stats['total_calls']}
- 缓存命中: {stats['cache_hits']}
- 总token数: {stats['total_tokens']}
- 总成本: ${stats['total_cost']:.4f}
""")
```

### 调试模式

```python
# 启用调试模式
config = ParserConfig(
    enable_llm_assistance=True,
    llm_debug_mode=True,
    llm_save_prompts=True
)

# 调试信息会输出到日志
# prompt会保存到 .llm_prompts/ 目录
```

---

## 最佳实践

### 1. 何时启用LLM

✅ **建议启用**:
- 处理未知来源的书籍
- 特殊格式书籍(章回体、剧本等)
- 质量要求高的场景
- 用户反馈误识别问题

❌ **可以不启用**:
- 标准网文(准确率已经很高)
- 批量处理(成本考虑)
- 性能优先场景
- 离线环境

### 2. 成本控制建议

```python
# 设置合理的限制
config = ParserConfig(
    llm_max_calls_per_book=10,      # 防止失控
    llm_max_cost_per_book=0.10,     # 成本上限
    llm_cache_enabled=True          # 必须开启
)
```

### 3. 提高准确率

```python
# 提供更多上下文
doc_context = {
    'doc_type': '学术论文',
    'language': 'chinese',
    'known_pattern': '章节用罗马数字'
}

assistant.analyze_chapter_candidates(
    candidates,
    content,
    existing_chapters,
    doc_context=doc_context  # 传入上下文
)
```

### 4. 错误处理

```python
try:
    volumes = parser.parse(content)
except Exception as e:
    logger.error(f"LLM parsing failed: {e}")
    # 降级到纯规则解析
    volumes = parse_hierarchical_content(content)
```

---

## FAQ

### Q1: LLM会增加多少成本?

**A**: 平均每本书 $0.01-0.05,大部分书籍无需LLM ($0)。

### Q2: 会不会变慢很多?

**A**: 轻微变慢(1-4秒),但准确率提升显著(82%→95%)。

### Q3: 支持哪些LLM?

**A**: 主要支持Anthropic Claude,可扩展到其他支持JSON输出的LLM。

### Q4: 可以完全依赖LLM吗?

**A**: 不建议。规则+LLM混合模式性价比最高。

### Q5: 如何保护API密钥?

**A**: 使用环境变量或密钥管理服务,不要硬编码。

### Q6: 离线环境能用吗?

**A**: LLM功能需要在线,但可以降级到纯规则模式。

---

## 总结

### 核心优势

✅ **准确率提升**: 从82%提升到95%+
✅ **智能适应**: 自动处理特殊格式
✅ **成本可控**: 平均$0.02/本
✅ **渐进增强**: 不影响现有功能
✅ **易于集成**: 最少代码改动

### 技术亮点

- 混合策略(规则优先+LLM辅助)
- 置信度评分系统
- Prompt Caching成本优化
- 批量处理减少调用
- 结构化输出(JSON)

### 适用场景

适合需要高准确率的场景,特别是:
- 特殊格式书籍
- 质量要求高的转换
- 未知格式的文本
- 需要智能消歧的场景

---

## 附录

### A. Prompt Caching 详解

Anthropic的Prompt Caching可以缓存长的system提示词和上下文,大幅降低成本:

```
首次调用:
- 输入: 5000 tokens ($0.015)
- 输出: 500 tokens ($0.0075)
- 总成本: $0.0225

后续调用(缓存命中):
- 输入: 5000 tokens cached ($0.0015)  # 90% off
- 输出: 500 tokens ($0.0075)
- 总成本: $0.009

节省: 60% ⬇️
```

### B. 错误码说明

| 错误码 | 说明 | 处理方式 |
|-------|------|---------|
| LLM_001 | API调用失败 | 降级到规则解析 |
| LLM_002 | JSON解析失败 | 重试或跳过 |
| LLM_003 | 超出成本限制 | 停止LLM调用 |
| LLM_004 | 超时 | 重试或降级 |

### C. 性能优化清单

- [ ] 启用prompt caching
- [ ] 批量处理候选项
- [ ] 设置合理的置信度阈值
- [ ] 限制最大调用次数
- [ ] 使用高置信度跳过机制
- [ ] 缓存LLM响应(本地)
- [ ] 异步调用(可选)

---

## 更新日志

**v1.0.0** (2025-12-12)
- 初始设计文档
- 完整的架构和实现方案
- 详细的使用示例

---

## 相关资源

- [Anthropic API文档](https://docs.anthropic.com/)
- [Prompt Caching指南](https://docs.anthropic.com/claude/docs/prompt-caching)
- [OPTIMIZATION_README.md](OPTIMIZATION_README.md) - 已完成的优化
- [parser.py](tasks/txt-to-epub-core/parser.py) - 现有解析器
- [parser_config.py](tasks/txt-to-epub-core/parser_config.py) - 配置系统

---

**文档维护**: 请在实施过程中及时更新此文档
**反馈**: 欢迎提出改进建议和问题
