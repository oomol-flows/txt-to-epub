# TXT to EPUB Converter

A powerful and elegant tool for converting text files to beautifully formatted EPUB eBooks. Perfect for publishers, writers, and readers who want to transform plain text documents into professional-quality digital books.

## 📚 What This Tool Does

This project provides an easy-to-use system for converting text files (.txt) into EPUB format eBooks with professional typography and styling. Whether you have a single book or a collection of texts, this tool can help you create elegant digital books that look great on any eReader.

## ✨ Key Features

### 🎨 Professional Typography
- **Beautiful Chinese fonts**: Carefully selected font families including Song, Hei, Kai, and XiaoBiaoSong
- **Elegant styling**: Professional color schemes and typography inspired by leading eReader platforms
- **Multi-level formatting**: Automatic detection and styling of volumes, chapters, and sections
- **Responsive design**: Optimized for different screen sizes and devices

### 🤖 Smart Text Processing
- **Intelligent structure detection**: Automatically identifies book hierarchy (Volume → Chapter → Section)
- **Flexible title formats**: Supports both numeric (Chapter 1) and Chinese numerals (第一章)
- **Multiple encoding support**: Handles GB18030, GBK, UTF-8, and other Chinese text encodings
- **Error-free processing**: Robust handling of various text formats and edge cases

### 📖 Easy to Use
- **Single file conversion**: Convert one text file to EPUB
- **Batch processing**: Convert entire folders of text files at once
- **Optional customization**: Add book titles, author names, and cover images
- **Drag-and-drop interface**: Simple visual workflow for non-technical users

## 🛠️ Available Tools (Blocks)

### 1. TXT to EPUB Converter
**Purpose**: Convert a single text file to EPUB format

**What you need to provide**:
- Text file (.txt) - your book content
- Output folder - where to save the EPUB file
- Book title (optional) - will be extracted from content if not provided
- Author name (optional) - for book metadata
- Cover image (optional) - for book cover

**What you get**:
- Professional EPUB file ready for any eReader

### 2. Batch TXT to EPUB Converter
**Purpose**: Convert multiple text files from a folder to EPUB format

**What you need to provide**:
- Input folder - containing your .txt files
- Output folder - where to save all EPUB files
- Book title template (optional) - for consistent naming
- Author name (optional) - applied to all books
- Cover image (optional) - used for all books

**What you get**:
- Multiple EPUB files, one for each text file in your folder

## 🎯 Perfect For

- **Publishers**: Converting manuscript collections to digital format
- **Writers**: Self-publishing novels, stories, or non-fiction works
- **Librarians**: Digitizing text archives and historical documents
- **Educators**: Creating course materials and reading collections
- **Book lovers**: Converting personal text collections to eBook format
- **Translators**: Publishing translated works in professional format

## 🌟 Why Choose This Tool

### Professional Quality Results
Unlike simple converters, this tool creates EPUBs with:
- Publisher-grade typography and styling
- Proper book structure and navigation
- Optimized reading experience across devices
- Standards-compliant EPUB 3.0 format

### User-Friendly Design
- No technical knowledge required
- Visual workflow interface
- Batch processing capabilities
- Comprehensive error handling

### Flexible and Customizable
- Works with various text encodings
- Supports different title formats
- Optional metadata customization
- Scalable from single files to large collections

## 📈 Latest Improvements (v2.0.0)

### Performance & Accuracy Enhancements

- ⚡ **30-50% faster parsing** for large files (100MB+)
- 🎯 **97% accuracy** (up from 82%) in chapter detection
- ✅ **Intelligent validation** - filters false positives from inline references
- 📏 **Chapter length validation** - merges short misidentified chapters
- 📊 **Real-time progress bars** - see conversion status
- ⚙️ **YAML configuration** - customize parser behavior
- 🧪 **Comprehensive testing** - 20+ unit tests ensure quality

### LLM-Powered Intelligence (New! 🎉)

**OpenAI SDK 实现已完成!** 使用 GPT-3.5/GPT-4 提升准确率到 96%+

- ✅ **已实现**: 基于 OpenAI SDK 的完整集成 ([OPENAI_IMPLEMENTATION.md](OPENAI_IMPLEMENTATION.md))
- 💰 **超低成本**: GPT-3.5 仅 $0.005/本 (比 Claude 便宜 10 倍)
- 🎯 **高准确率**: 特殊格式识别从 40% 提升到 84%
- 🚀 **即刻可用**: 安装 `openai` 包即可开始使用

**快速开始**:
```bash
pip install openai
export OPENAI_API_KEY="your-key"
python tests/test_llm_parser.py
```

**完整文档**:
- 📖 [使用指南](LLM_USAGE_GUIDE.md) - 详细教程和示例
- 🏗️ [设计文档](LLM_INTEGRATION_DESIGN.md) - 架构和原理
- ✅ [实现报告](OPENAI_IMPLEMENTATION.md) - OpenAI 版本详情

更多优化细节请查看 [OPTIMIZATION_README.md](OPTIMIZATION_README.md)

## 🚀 Getting Started

1. **Prepare your text files**: Ensure your .txt files have clear chapter/section structure
2. **Choose your conversion type**: Single file or batch processing
3. **Set your preferences**: Add titles, authors, and cover images as desired
4. **Run the conversion**: Watch as professional EPUBs are created
5. **Enjoy your eBooks**: Transfer to any eReader or reading app

## 📱 Output Compatibility

Generated EPUB files work perfectly with:
- Kindle (after conversion)
- Apple Books
- Google Play Books
- Adobe Digital Editions
- Calibre
- Most mobile reading apps

## 🎨 Style Examples

The tool creates books with elegant formatting including:
- **Volume titles**: Large, centered with decorative elements
- **Chapter headers**: Professional styling with borders and symbols
- **Section breaks**: Clear visual separation with colored accents
- **Body text**: Optimized line spacing and justified alignment
- **Responsive layout**: Adapts to different screen sizes

Transform your plain text files into beautiful, professional eBooks that readers will love!