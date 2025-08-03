#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：生成带有精美样式的EPUB文件
"""

import sys
import os

# 添加路径以便导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'tasks', 'txt-to-epub'))

try:
    # 导入模块中的函数
    import importlib.util
    module_path = os.path.join(os.path.dirname(__file__), 'tasks', 'txt-to-epub', '__init__.py')
    spec = importlib.util.spec_from_file_location("txt_to_epub", module_path)
    if spec and spec.loader:
        txt_to_epub_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(txt_to_epub_module)
        txt_to_epub = txt_to_epub_module.txt_to_epub
    else:
        raise ImportError("无法加载模块")
    
    # 测试参数
    txt_file = os.path.join(os.path.dirname(__file__), 'test_content.txt')
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    epub_file = os.path.join(output_dir, 'test_styled_book.epub')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成EPUB文件
    print("正在生成精美样式的EPUB文件...")
    txt_to_epub(
        txt_file=txt_file,
        epub_file=epub_file,
        title='测试书籍 - 精美样式版',
        author='样式测试作者'
    )
    
    print(f"EPUB文件已生成: {epub_file}")
    print("可以使用电子书阅读器查看样式效果")
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所需的依赖包:")
    print("pip install EbookLib chardet")
except Exception as e:
    print(f"生成EPUB时出错: {e}")
