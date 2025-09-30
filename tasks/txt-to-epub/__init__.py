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
    epub_file: typing.NotRequired[str]
#endregion
 
# Import core conversion functionality
from .core import txt_to_epub

# Simplified logging configuration
logger = logging.getLogger(__name__)


def main(params: Inputs, context: Context) -> Outputs:
    """
    Main function: Convert text file to EPUB format ebook
    
    This is a simplified version focusing on core functionality with reduced complex API exposure.

    Args:
        params: Input parameter dictionary, required parameters: txt_file, epub_dir
        context: Context object
        
    Returns:
        Dictionary containing the generated EPUB file path
    """
    # Validate required parameters
    txt_file = params.get('txt_file')
    epub_dir = params.get('epub_dir')
    
    if not txt_file or not epub_dir:
        logger.error("Missing required parameters: both txt_file and epub_dir cannot be empty")
        return {
            "epub_file": "",
            "validation_passed": False,
            "validation_report": "Conversion failed: missing required parameters",
            "volumes_count": 0,
            "chapters_count": 0
        }
    
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
        epub_file = os.path.join(epub_dir, f"{book_title}.epub")
        
        # Execute conversion
        logger.info(f"Starting conversion: {txt_file} -> {epub_file}")
        result = txt_to_epub(
            txt_file=txt_file,
            epub_file=epub_file,
            title=book_title,
            author=author,
            cover_image=cover_image
        )
        
        logger.info(f"Conversion completed: {epub_file}")
        context.preview({
            "type": "markdown",
            "data": result["validation_report"]
        })
        # Return complete result information
        return {
            "epub_file": result["output_file"],
        }
        
    except Exception as e:
        logger.error(f"Error occurred during conversion: {e}")
        context.preview({
            "type": "markdown",
            "data":  f"Conversion failed: {str(e)}"
        })
        return {
            "epub_file": ""
        }
