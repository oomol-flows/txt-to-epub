#!/usr/bin/env python3

"""
多语言书籍解析演示
展示txt-to-epub解析器对中英文书籍的支持
"""

import sys
import os
sys.path.append('/app/workspace/tasks/txt-to-epub')

from data_structures import Section, Chapter, Volume
from parser import detect_language, parse_hierarchical_content

def demo_parsing(file_path, language_name):
    """演示书籍解析过程"""
    print(f"\n{'='*60}")
    print(f"📚 {language_name}书籍解析演示")
    print(f"文件：{os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 语言检测
        detected_language = detect_language(content)
        print(f"🔍 语言检测结果: {detected_language}")
        print(f"📄 文档长度: {len(content)} 字符")
        
        # 2. 解析层次结构
        print(f"\n📖 开始解析层次结构...")
        volumes = parse_hierarchical_content(content)
        
        print(f"✅ 解析完成！")
        print(f"📚 总卷数: {len(volumes)}")
        
        total_chapters = sum(len(vol.chapters) for vol in volumes)
        total_sections = sum(len(chap.sections) for vol in volumes for chap in vol.chapters)
        print(f"📄 总章数: {total_chapters}")
        print(f"📝 总节数: {total_sections}")
        
        # 3. 显示结构详情
        print(f"\n📋 书籍结构详情:")
        
        for vol_idx, volume in enumerate(volumes, 1):
            if volume.title:
                vol_display = f"📘 {volume.title}"
            else:
                vol_display = f"📘 卷 {vol_idx}"
            
            print(f"\n{vol_display} ({len(volume.chapters)} 章)")
            
            for chap_idx, chapter in enumerate(volume.chapters, 1):
                # 显示章节
                chapter_prefix = "  📝" if chap_idx <= 3 else "  ..."
                if chap_idx <= 3:  # 只显示前3章的详情
                    print(f"{chapter_prefix} 第{chap_idx}章: {chapter.title}")
                    
                    # 显示内容预览
                    if chapter.content:
                        content_preview = chapter.content[:80].replace('\n', ' ').strip()
                        print(f"      💭 内容: {content_preview}...")
                    
                    # 显示节信息
                    if chapter.sections:
                        print(f"      📚 包含 {len(chapter.sections)} 个节:")
                        for sec_idx, section in enumerate(chapter.sections[:2], 1):  # 只显示前2节
                            print(f"        📄 {sec_idx}. {section.title}")
                elif chap_idx == 4:
                    print("  ... (更多章节)")
        
        # 4. 统计信息
        print(f"\n📊 解析统计:")
        avg_chapter_length = sum(len(chap.content) for vol in volumes for chap in vol.chapters) / total_chapters if total_chapters > 0 else 0
        print(f"  • 平均章节长度: {avg_chapter_length:.0f} 字符")
        
        chapters_with_sections = sum(1 for vol in volumes for chap in vol.chapters if chap.sections)
        print(f"  • 包含节的章节数: {chapters_with_sections}")
        
        return True
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主演示函数"""
    print("🌟 txt-to-epub 多语言书籍解析器演示")
    print("支持中英文书籍的智能解析")
    
    # 测试文件列表
    test_files = [
        ("/oomol-driver/oomol-storage/book/伯特兰·罗素：哲学问题.txt", "中文"),
        ("/oomol-driver/oomol-storage/book/Pride_and_Prejudice_Sample.txt", "英文")
    ]
    
    results = []
    
    for file_path, language_name in test_files:
        if os.path.exists(file_path):
            result = demo_parsing(file_path, language_name)
            results.append((language_name, result))
        else:
            print(f"❌ 文件不存在: {file_path}")
            results.append((language_name, False))
    
    # 总结
    print(f"\n{'='*60}")
    print("🎯 演示总结")
    print(f"{'='*60}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for language_name, result in results:
        status = "✅ 成功" if result else "❌ 失败"
        print(f"{status} {language_name}书籍解析")
    
    print(f"\n📈 成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 所有演示完成！txt-to-epub解析器已成功支持中英文书籍。")
        print("\n✨ 新功能特性:")
        print("  🔍 自动语言检测")
        print("  📚 中英文目录识别与移除")
        print("  📖 多种章节格式支持")
        print("  📝 智能节结构解析")
        print("  🌐 完整的多语言兼容性")
    else:
        print("⚠️  部分演示失败，需要进一步优化。")

if __name__ == "__main__":
    main()