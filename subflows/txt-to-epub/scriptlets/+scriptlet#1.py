from oocana import Context
import requests
import os
import uuid

#region generated meta
import typing
class Inputs(typing.TypedDict):
    cover_image: str | None
    cover_url: str | None
class Outputs(typing.TypedDict):
    cover_image: typing.NotRequired[str | None]
#endregion

def main(params: Inputs, context: Context) -> Outputs | None:
    # 优先使用 cover_image，其次下载 cover_url
    cover_image = params.get('cover_image')
    if cover_image:
        return {
            "cover_image": cover_image
        }
    
    cover_url = params.get('cover_url')
    if cover_url:
        try:
            # 下载图片到本地
            response = requests.get(cover_url, timeout=30)
            response.raise_for_status()
            
            # 生成唯一的文件名
            file_extension = os.path.splitext(cover_url)[1] or '.jpg'
            file_name = f"cover_{uuid.uuid4().hex}{file_extension}"
            
            # 保存到工作目录
            file_path = os.path.join(context.session_dir, file_name)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return {
                "cover_image": file_path
            }
        except Exception as e:
            context.log(f"下载封面图片失败: {str(e)}")
            return None
    
    # 如果两个参数都不存在，返回 None
    return None