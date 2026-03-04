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
    enable_ai_metadata: bool | None
    enable_ai_cover: bool | None
    enable_ai_illustrations: bool | None
    illustration_density: typing.Literal["low", "medium", "high", "ultra"] | None
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

# Import library functions
from txt_to_epub import txt_to_epub, ParserConfig

# Configure logging
logger = logging.getLogger(__name__)


def main(params: Inputs, context: Context) -> Outputs:
    """
    Main function: Convert text file to EPUB format ebook

    Uses the txt-to-epub-converter library for conversion.

    Args:
        params: Input parameter dictionary, required parameter: txt_file
        context: Context object

    Returns:
        Dictionary containing the generated EPUB file path
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("========== TXT to EPUB Conversion Started ==========")

    # Report initial progress
    context.report_progress(0)

    # Validate required parameters
    txt_file = params.get('txt_file')
    if not txt_file:
        logger.error("Missing required parameter: txt_file")
        raise ValueError("Conversion failed: txt_file cannot be empty")

    try:
        # Generate book title (use filename if not provided)
        book_title = params.get('book_title')
        if not book_title:
            txt_filename = os.path.basename(txt_file)
            book_title = os.path.splitext(txt_filename)[0]

        # Set default values for optional parameters
        # Pass empty string if no author provided - library will skip showing "Unknown Author"
        author = params.get('author') or ''
        cover_image = params.get('cover_image')  # None if not provided

        # Generate output file path
        epub_file_param = params.get('epub_file')
        if epub_file_param and epub_file_param.strip():
            epub_file = epub_file_param
        else:
            epub_file = os.path.join(context.session_dir, f"{book_title}.epub")

        # Smart TOC settings with defaults
        enable_smart_toc = params.get('enable_smart_toc')
        if enable_smart_toc is None:
            enable_smart_toc = True

        # LLM configuration with defaults
        llm_config = params.get('llm') or {
            'model': 'oomol-chat',
            'temperature': 0.5,
            'top_p': 1,
            'max_tokens': 128000
        }

        # Threshold parameters with defaults
        llm_confidence_threshold = params.get('llm_confidence_threshold')
        if llm_confidence_threshold is None:
            llm_confidence_threshold = 0.5

        llm_toc_detection_threshold = params.get('llm_toc_detection_threshold')
        if llm_toc_detection_threshold is None:
            llm_toc_detection_threshold = 0.5

        llm_no_toc_threshold = params.get('llm_no_toc_threshold')
        if llm_no_toc_threshold is None:
            llm_no_toc_threshold = 0.6

        toc_detection_score_threshold = params.get('toc_detection_score_threshold')
        if toc_detection_score_threshold is None:
            toc_detection_score_threshold = 20

        toc_max_scan_lines = params.get('toc_max_scan_lines')
        if toc_max_scan_lines is None:
            toc_max_scan_lines = 300

        enable_resume = params.get('enable_resume')
        if enable_resume is None:
            enable_resume = True

        # AI cover and illustrations settings
        enable_ai_cover = params.get('enable_ai_cover')
        if enable_ai_cover is None:
            enable_ai_cover = True

        enable_ai_illustrations = params.get('enable_ai_illustrations')
        if enable_ai_illustrations is None:
            enable_ai_illustrations = True

        # AI metadata settings (auto-detect author and title)
        enable_ai_metadata = params.get('enable_ai_metadata')
        if enable_ai_metadata is None:
            enable_ai_metadata = True

        # Illustration density settings (0.2.0: use density directly)
        illustration_density = params.get('illustration_density', 'medium')

        # Log configuration
        logger.info(f"Book Title: {book_title}")
        logger.info(f"Author: {author or 'Not provided (AI will detect)'}")
        logger.info(f"Cover Image: {cover_image or 'None'}")
        logger.info(f"Smart TOC: {enable_smart_toc}")
        logger.info(f"AI Metadata: {enable_ai_metadata}")
        logger.info(f"AI Cover: {enable_ai_cover}")
        logger.info(f"AI Illustrations: {enable_ai_illustrations}")
        if enable_ai_illustrations:
            logger.info(f"Illustration Density: {illustration_density}")
        logger.info(f"LLM Model: {llm_config.get('model', 'oomol-chat')}")
        logger.info(f"Confidence Threshold: {llm_confidence_threshold}")
        logger.info(f"Resume Enabled: {enable_resume}")

        # Determine if LLM is needed (for smart TOC or AI features)
        need_llm = enable_smart_toc or enable_ai_cover or enable_ai_illustrations or enable_ai_metadata

        # Configure parser using library's ParserConfig
        config = ParserConfig(
            enable_llm_assistance=enable_smart_toc,
            llm_api_key=context.oomol_llm_env.get("api_key") if need_llm else None,
            llm_base_url=context.oomol_llm_env.get("base_url_v1") if need_llm else None,
            llm_model=llm_config.get('model', 'oomol-chat') if need_llm else 'oomol-chat',
            llm_confidence_threshold=llm_confidence_threshold,
            llm_toc_detection_threshold=llm_toc_detection_threshold,
            llm_no_toc_threshold=llm_no_toc_threshold,
            toc_detection_score_threshold=toc_detection_score_threshold,
            toc_max_scan_lines=toc_max_scan_lines,
            # AI metadata, cover and illustrations settings
            enable_ai_metadata=enable_ai_metadata,
            enable_ai_cover=enable_ai_cover,
            enable_ai_illustrations=enable_ai_illustrations,
            ai_illustration_density=illustration_density  # 0.2.0: use density directly
        )

        # Execute conversion using library function
        logger.info(f"Starting conversion: {txt_file} -> {epub_file}")
        result = txt_to_epub(
            txt_file=txt_file,
            epub_file=epub_file,
            title=book_title,
            author=author,
            cover_image=cover_image,
            config=config,
            context=context,
            enable_resume=enable_resume
        )

        # Preview validation report
        context.preview({
            "type": "markdown",
            "data": result["validation_report"]
        })
        logger.info(f"Conversion completed: {epub_file}")

        # Return result
        return {
            "epub_file": result["output_file"],
        }

    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        raise RuntimeError(f"Conversion failed: {str(e)}") from e
