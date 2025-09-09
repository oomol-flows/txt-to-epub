# TXT to EPUB Converter - Elegant Style Edition

A tool for converting TXT format text files to EPUB eBooks with elegant typography design.

## Key Features

### 🎨 Elegant Style Design
Inspired by professional typography styles from multi-platform e-readers, providing:

- **Hierarchical Title System**
  - Volume/Part/Book titles: Using XiaoBiaoSong font with decorative lines and gradient effects
  - Chapter titles: Center-aligned with bottom decorative symbols
  - Section titles: Left colored border with gradient background effects

- **Elegant Font Combinations**
  - Body text: Song family fonts (DK-SONGTI, FangZheng Song San, FangZheng Shu Song, etc.)
  - Titles: XiaoBiaoSong fonts (DK-XIAOBIAOSONG, FangZheng XiaoBiaoSong, etc.)
  - Emphasis: Hei family fonts (DK-HEITI, FangZheng LanTing Hei, etc.)
  - Quotes: Kai family fonts (DK-KAITI, FangZheng Kai, HuaWen Kai, etc.)

- **Professional Color Scheme**
  - Primary color: #91531d (warm brown)
  - Chapter titles: #1f4a92 (deep blue)
  - Section titles: #478686 (teal green)
  - Body text: #2c2c2c (dark gray)

- **Exquisite Visual Elements**
  - Decorative dividers and symbols
  - Gradient backgrounds and shadow effects
  - Responsive design for different screen sizes
  - Optimized Chinese typography

### 📚 Intelligent Text Parsing
- **Three-level hierarchy**: Auto-detect Volume/Part/Book → Chapter → Section
- **Flexible title formats**: Support numeric and Chinese numerals (including traditional)
- **Smart encoding detection**: Auto-handle GB18030, GBK, UTF-8 and other encodings

### 🛠️ Usage

#### Basic Usage
```python
from tasks.txt_to_epub import txt_to_epub

txt_to_epub(
    txt_file="input.txt",
    epub_file="output.epub",
    title="My Book",
    author="Author Name",
    cover_image="cover.jpg"  # optional
)
```

#### As Workflow Task
```python
from tasks.txt_to_epub import main
from oocana import Context

params = {
    'txt_file': 'input.txt',
    'epub_dir': 'output/',
    'book_title': 'My Book',      # optional
    'author': 'Author Name',      # optional
    'cover_image': 'cover.jpg'    # optional
}

result = main(params, Context())
```

### 📖 Supported Text Formats

#### Title Recognition Patterns
- **Volume-level titles**: Volume One/Part One/Book One + title
- **Chapter-level titles**: Chapter One + title
- **Section-level titles**: Section One + title

#### Example Text Structure
```
Volume One: Opening Chapter

Chapter 1: Beginning
This is chapter content...

Section 1: Character Introduction
This is section content...

Section 2: Background Setting
This is another section's content...

Chapter 2: Development
This is chapter content without subsections...
```

### 🎨 Style Features

#### Volume Title Style
- XiaoBiaoSong font, 2.4em size
- Warm brown theme (#91531d)
- Bottom decorative lines with gradient effects
- Center-aligned with ample top and bottom margins

#### Chapter Title Style
- XiaoBiaoSong font, 2em size
- Deep blue theme (#1f4a92)
- Bottom border line with decorative symbols
- Center-aligned with elegant spacing

#### Section Title Style
- Hei font, 1.4em size
- Teal green theme (#478686)
- Left colored border with gradient background
- Left-aligned with prefix decorative symbols

#### Body Text Style
- Song font 16px, line height 1.8
- First line indent 2 characters
- Justified alignment with optimized spacing
- Dark gray text (#2c2c2c)

### 📱 Responsive Design
- Tablet device adaptation (below 768px)
- Mobile device adaptation (below 480px)
- Print style optimization
- Chinese typography optimization

### 🔧 Technical Features
- **Auto encoding detection**: Support GB18030, GBK, UTF-8, etc.
- **Error handling**: Comprehensive exception handling and logging
- **Memory optimization**: Efficient text processing and EPUB generation
- **Standard compliance**: Compliant with EPUB 3.0 standard

### 📦 Dependencies
```
EbookLib==0.18
chardet==5.2.0
```

### 🚀 Quick Test
Run test script to generate sample EPUB:
```bash
python test_epub_generation.py
```

### 💡 Style Inspiration
The style design of this tool is inspired by:
- [DuoKan Reader's CSS templates](https://github.com/Eninix/sigil-template)
- Professional publishing typography standards
- Modern eBook visual design trends

Generated EPUB files will display optimal visual effects on CSS-supporting readers, especially in applications that support DuoKan format like Xiaomi Reader.