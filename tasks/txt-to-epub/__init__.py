import os
import logging
from oocana import Context

#region generated meta
import typing
from oocana import LLMModelOptions
class Inputs(typing.TypedDict):
    txt_file: str
    epub_file: str | None
    book_title: str | None
    author: str | None
    cover_image: str | None
    enable_smart_toc: bool | None
    llm_confidence_threshold: float | None
    llm_toc_detection_threshold: float | None
    llm_no_toc_threshold: float | None
    toc_detection_score_threshold: float | None
    toc_max_scan_lines: int | None
    enable_resume: bool | None
    llm: LLMModelOptions
class Outputs(typing.TypedDict):
    epub_file: typing.NotRequired[str]
#endregion
 
# Import core conversion functionality
from .core import txt_to_epub
from .parser_config import ParserConfig

# Simplified logging configuration
logger = logging.getLogger(__name__)


def main(params: Inputs, context: Context) -> Outputs:
    """
    Main function: Convert text file to EPUB format ebook

    This is a simplified version focusing on core functionality with reduced complex API exposure.

    Args:
        params: Input parameter dictionary, required parameter: txt_file
        context: Context object

    Returns:
        Dictionary containing the generated EPUB file path
    """
    # Configure logging at the very beginning
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("========== TXT to EPUB 转换开始 ==========")
    print("========== TXT to EPUB 转换开始 ==========")  # 强制输出,确保代码执行到这里

    # 上报初始进度
    context.report_progress(0)

    # Validate required parameters
    txt_file = params.get('txt_file')

    if not txt_file:
        logger.error("Missing required parameter: txt_file cannot be empty")
        raise ValueError("Conversion failed: txt_file cannot be empty")

    try:
        # Generate book title (use filename if not provided)
        book_title = params.get('book_title')
        if not book_title:
            txt_filename = os.path.basename(txt_file)
            book_title = os.path.splitext(txt_filename)[0]

        # Set default values for other parameters
        author = params.get('author') or 'Unknown Author'
        cover_image = params.get('cover_image')  # Can be None

        # Generate output file path
        epub_file_param = params.get('epub_file')
        if epub_file_param:
            epub_file = epub_file_param
        else:
            # Default to session directory with book title as filename
            epub_file = os.path.join(context.session_dir, f"{book_title}.epub")

        # Get smart TOC setting with recommended defaults
        enable_smart_toc = params.get('enable_smart_toc')
        if enable_smart_toc is None:
            enable_smart_toc = True  # Recommended default: enable smart TOC

        # Get LLM thresholds with recommended defaults
        llm_confidence_threshold = params.get('llm_confidence_threshold')
        if llm_confidence_threshold is None:
            llm_confidence_threshold = 0.5  # Recommended default

        llm_toc_detection_threshold = params.get('llm_toc_detection_threshold')
        if llm_toc_detection_threshold is None:
            llm_toc_detection_threshold = 0.5  # Recommended default

        llm_no_toc_threshold = params.get('llm_no_toc_threshold')
        if llm_no_toc_threshold is None:
            llm_no_toc_threshold = 0.6  # Recommended default

        toc_detection_score_threshold = params.get('toc_detection_score_threshold')
        if toc_detection_score_threshold is None:
            toc_detection_score_threshold = 20  # Recommended default

        toc_max_scan_lines = params.get('toc_max_scan_lines')
        if toc_max_scan_lines is None:
            toc_max_scan_lines = 300  # Recommended default

        enable_resume = params.get('enable_resume')
        if enable_resume is None:
            enable_resume = True  # Recommended default: enable resume

        llm_config = params.get('llm')
        if llm_config is None:
            llm_config = {
                'model': 'oomol-chat',
                'temperature': 0.5,
                'top_p': 1,
                'max_tokens': 128000
            }  # Recommended defaults

        # Debug logging
        print(f"=== 配置调试信息 (print) ===")
        print(f"params中的enable_smart_toc值: {params.get('enable_smart_toc')}")
        print(f"实际enable_smart_toc: {enable_smart_toc}")
        print(f"LLM置信度阈值: {llm_confidence_threshold}")
        print(f"LLM目录检测置信度阈值: {llm_toc_detection_threshold}")
        print(f"LLM无目录判定置信度阈值: {llm_no_toc_threshold}")
        print(f"目录检测评分阈值: {toc_detection_score_threshold}")
        print(f"目录最大扫描行数: {toc_max_scan_lines}")
        print(f"llm_config: {llm_config}")

        logger.info(f"=== 配置调试信息 ===")
        logger.info(f"params中的enable_smart_toc值: {params.get('enable_smart_toc')}")
        logger.info(f"实际enable_smart_toc: {enable_smart_toc}")
        logger.info(f"LLM置信度阈值: {llm_confidence_threshold}")
        logger.info(f"LLM目录检测置信度阈值: {llm_toc_detection_threshold}")
        logger.info(f"LLM无目录判定置信度阈值: {llm_no_toc_threshold}")
        logger.info(f"目录检测评分阈值: {toc_detection_score_threshold}")
        logger.info(f"目录最大扫描行数: {toc_max_scan_lines}")
        logger.info(f"llm_config: {llm_config}")

        # Log smart TOC setting
        if enable_smart_toc:
            logger.info(f"智能目录分析: 已启用 (模型: {llm_config.get('model', 'deepseek-v3.2')}, 阈值: {llm_confidence_threshold})")
        else:
            logger.info("智能目录分析: 未启用,使用传统规则解析")

        # Configure parser
        config = ParserConfig(
            enable_llm_assistance=enable_smart_toc,
            llm_api_key=context.oomol_llm_env.get("api_key") if enable_smart_toc else None,
            llm_base_url=context.oomol_llm_env.get("base_url_v1") if enable_smart_toc else None,
            llm_model=llm_config.get('model', 'deepseek-v3.2') if enable_smart_toc else 'deepseek-v3.2',
            llm_confidence_threshold=llm_confidence_threshold,
            llm_toc_detection_threshold=llm_toc_detection_threshold,
            llm_no_toc_threshold=llm_no_toc_threshold,
            toc_detection_score_threshold=toc_detection_score_threshold,
            toc_max_scan_lines=toc_max_scan_lines
        )
        # Execute conversion
        logger.info(f"Starting conversion: {txt_file} -> {epub_file}")
        result = txt_to_epub(
            txt_file=txt_file,
            epub_file=epub_file,
            title=book_title,
            author=author,
            cover_image=cover_image,
            config=config,
            context=context,  # 传递 context 用于进度上报
            enable_resume=enable_resume  # 传递断点续传配置
        )
        context.preview({
            "type": "markdown",
            "data": result["validation_report"]
        })
        logger.info(f"Conversion completed: {epub_file}")

        # Return complete result information
        return {
            "epub_file": result["output_file"],
        }

    except Exception as e:
        logger.error(f"Error occurred during conversion: {e}")
        raise RuntimeError(f"Conversion failed: {str(e)}") from e
