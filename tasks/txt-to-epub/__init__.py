import os
import logging
from oocana import Context

#region generated meta
import typing
class Inputs(typing.TypedDict):
    txt_file: str
    epub_dir: str
    book_title: str | None
    author: str | None
    cover_image: str | None
class Outputs(typing.TypedDict):
    epub_file: str
#endregion

# 导入核心转换功能
from .core import txt_to_epub

# 简化日志配置
logger = logging.getLogger(__name__)


def main(params: Inputs, context: Context) -> Outputs:
    """
    主函数：将文本文件转换为EPUB格式的电子书
    
    这是简化版本，专注于核心功能，减少了复杂的API暴露。

    Args:
        params: 输入参数字典，必需参数：txt_file, epub_dir
        context: 上下文对象
        
    Returns:
        包含生成的EPUB文件路径的字典
    """
    # 验证必需参数
    txt_file = params.get('txt_file')
    epub_dir = params.get('epub_dir')
    
    if not txt_file or not epub_dir:
        logger.error("缺少必需参数：txt_file 和 epub_dir 都不能为空")
        return {"epub_file": ""}
    
    try:
        # 生成书籍标题（如果未提供则使用文件名）
        book_title = params.get('book_title')
        if not book_title:
            txt_filename = os.path.basename(txt_file)
            book_title = os.path.splitext(txt_filename)[0]
        
        # 设置其他参数的默认值
        author = params.get('author') or '未知作者'
        cover_image = params.get('cover_image')  # 可为None
        
        # 生成输出文件路径
        epub_file = os.path.join(epub_dir, f"{book_title}.epub")
        
        # 执行转换
        logger.info(f"开始转换: {txt_file} -> {epub_file}")
        txt_to_epub(
            txt_file=txt_file,
            epub_file=epub_file,
            title=book_title,
            author=author,
            cover_image=cover_image
        )
        
        logger.info(f"转换完成: {epub_file}")
        return {"epub_file": epub_file}
        
    except Exception as e:
        logger.error(f"转换过程中发生错误: {e}")
        return {"epub_file": ""}
