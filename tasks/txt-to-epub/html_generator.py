from ebooklib import epub
from typing import Optional


def create_volume_page(volume_title: str, file_name: str, chapter_count: int) -> epub.EpubHtml:
    """
    创建卷/部/篇的页面，使用现代化设计。
    
    :param volume_title: 卷标题
    :param file_name: 文件名
    :param chapter_count: 章节数量
    :return: EpubHtml对象
    """
    volume_page = epub.EpubHtml(title=volume_title, file_name=file_name, lang='zh')
    
    # 确定单位名称和装饰图标
    if "卷" in volume_title:
        unit_name = "卷"
        icon = "📖"
    elif "部" in volume_title:
        unit_name = "部"
        icon = "📚"
    elif "篇" in volume_title:
        unit_name = "篇"
        icon = "📜"
    else:
        unit_name = "卷"
        icon = "📖"
    
    # 创建简洁的卷页面内容
    volume_page.content = f'''
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{volume_title}</title>
        <link rel="stylesheet" type="text/css" href="style/nav.css"/>
    </head>
    <body class="chinese-text">
        <h1 class="volume-title">{volume_title}</h1>
        <div style="margin-top: 3rem; text-align: center;">
            <div style="font-size: 3em; margin-bottom: 2rem;">{icon}</div>
            <p style="color: #2c3e50; font-size: 1.3em; font-weight: 500; margin-bottom: 4rem;">
                本{unit_name}包含 {chapter_count} 章内容
            </p>
            <div style="position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%); width: 100%;">
                <p style="color: #95a5a6; font-size: 0.8em; text-align: center;">
                    oomol.com 开源工作组提供格式转换工具，请用户确保版权合规
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return volume_page



def create_chapter_page(chapter_title: str, chapter_content: str, file_name: str, section_count: int) -> epub.EpubHtml:
    """
    创建章节页面（用于有小节的章节），使用现代化设计。
    
    :param chapter_title: 章节标题
    :param chapter_content: 章节内容（通常为空，因为内容在小节中）
    :param file_name: 文件名
    :param section_count: 小节数量
    :return: EpubHtml对象
    """
    chapter_page = epub.EpubHtml(title=chapter_title, file_name=file_name, lang='zh')
    
    # 创建优雅的章节页面内容
    if chapter_content.strip():
        chapter_page.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{chapter_title}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <h1 class="chapter-title">{chapter_title}</h1>
            <div style="margin-top: 1.5rem;">
                <pre>{chapter_content}</pre>
            </div>
            
            <div style="margin-top: 3rem; text-align: center;">
                <div style="font-size: 3em; margin-bottom: 2rem;">📚</div>
                <p style="color: #2c3e50; font-size: 1.3em; font-weight: 500; margin-bottom: 4rem;">
                    本章包含 {section_count} 个小节
                </p>
                <div style="position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%); width: 100%;">
                    <p style="color: #95a5a6; font-size: 0.8em; text-align: center;">
                        oomol.com 开源工作组提供格式转换工具，请用户确保版权合规
                    </p>
                </div>
            </div>
        </body>
        </html>
        '''
    else:
        chapter_page.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{chapter_title}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <h1 class="chapter-title">{chapter_title}</h1>
            <div style="margin-top: 3rem; text-align: center;">
                <div style="font-size: 3em; margin-bottom: 2rem;">📚</div>
                <p style="color: #2c3e50; font-size: 1.3em; font-weight: 500; margin-bottom: 4rem;">
                    本章共分为 {section_count} 个小节
                </p>
                <div style="position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%); width: 100%;">
                    <p style="color: #95a5a6; font-size: 0.8em; text-align: center;">
                        oomol.com 开源工作组提供格式转换工具，请用户确保版权合规
                    </p>
                </div>
            </div>
        </body>
        </html>
        '''
    
    return chapter_page



def create_section_page(section_title: str, section_content: str, file_name: str) -> epub.EpubHtml:
    """
    创建节页面，使用现代化设计。
    
    :param section_title: 节标题
    :param section_content: 节内容
    :param file_name: 文件名
    :return: EpubHtml对象
    """
    section_page = epub.EpubHtml(title=section_title, file_name=file_name, lang='zh')
    
    if section_title:
        section_page.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{section_title}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <h2 class="section-title">{section_title}</h2>
            <div style="margin-top: 1rem;">
                <pre>{section_content}</pre>
            </div>
        </body>
        </html>
        '''
    else:
        # 无标题的节（章节序言）
        section_page.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>章节序言</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <div style="margin-top: 1rem;">
                <pre>{section_content}</pre>
            </div>
        </body>
        </html>
        '''
    
    return section_page



def create_chapter(title: str, content: str, file_name: str) -> epub.EpubHtml:
    """
    创建EPUB章节，使用现代化设计。
    """
    chapter = epub.EpubHtml(title=title, file_name=file_name, lang='zh')
    
    if content:
        chapter.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <h1 class="chapter-title">{title}</h1>
            <div style="margin-top: 1.5rem;">
                <pre>{content}</pre>
            </div>
        </body>
        </html>
        '''
    else:
        chapter.content = f'''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body class="chinese-text">
            <h1 class="chapter-title">{title}</h1>
        </body>
        </html>
        '''
    
    return chapter