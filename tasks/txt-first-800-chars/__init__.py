#region generated meta
import typing
class Inputs(typing.TypedDict):
    txt_file: str
class Outputs(typing.TypedDict):
    first_800_chars: typing.NotRequired[str]
    filename: typing.NotRequired[str]
#endregion

from oocana import Context
import os
import chardet

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

        # Detect file encoding using chardet
        with open(txt_file_path, 'rb') as file:
            raw_data = file.read()
            encoding_result = chardet.detect(raw_data)
            encoding = encoding_result.get('encoding', 'utf-8') or 'utf-8'
            confidence = encoding_result.get('confidence', 0)

            # If confidence is low, try common encodings
            if confidence < 0.7:
                common_encodings = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'big5', 'shift_jis', 'iso-8859-1']

                for enc in common_encodings:
                    try:
                        content = raw_data.decode(enc)
                        # If successful, use this encoding
                        encoding = enc
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # If all encodings fail, try with error handling
                    content = raw_data.decode('utf-8', errors='ignore')
            else:
                # Use detected encoding with error handling
                content = raw_data.decode(encoding, errors='ignore')

        # Extract first 800 characters
        first_800_chars = content[:800]

        return {
            "first_800_chars": first_800_chars,
            "filename": filename
        }

    except FileNotFoundError:
        raise ValueError(f"File not found: {txt_file_path}")
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")