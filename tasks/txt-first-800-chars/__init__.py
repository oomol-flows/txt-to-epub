#region generated meta
import typing
class Inputs(typing.TypedDict):
    txt_file: str
class Outputs(typing.TypedDict):
    first_800_chars: str
    filename: str
#endregion

from oocana import Context
import os

def main(params: Inputs, context: Context) -> Outputs:
    """
    Extract the first 800 characters from a txt file

    Args:
        params: Input parameter dictionary containing txt_file path
        context: OOMOL context object

    Returns:
        Output result dictionary with first 800 characters and filename
    """
    txt_file_path = params["txt_file"]

    try:
        # Extract filename from path
        filename = os.path.basename(txt_file_path)

        # Read the file with UTF-8 encoding
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Extract first 800 characters
        first_800_chars = content[:800]

        return {
            "first_800_chars": first_800_chars,
            "filename": filename
        }

    except FileNotFoundError:
        raise ValueError(f"File not found: {txt_file_path}")
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        try:
            filename = os.path.basename(txt_file_path)
            with open(txt_file_path, 'r', encoding='gb2312') as file:
                content = file.read()
            first_800_chars = content[:800]
            return {
                "first_800_chars": first_800_chars,
                "filename": filename
            }
        except UnicodeDecodeError:
            raise ValueError(f"Unable to decode file: {txt_file_path}")
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")