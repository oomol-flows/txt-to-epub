from oocana import Context

#region generated meta
import typing
class Inputs(typing.TypedDict):
    cover_image: str | None
    download_cover: str | None
class Outputs(typing.TypedDict):
    cover_image: typing.NotRequired[str | None]
#endregion

def main(params: Inputs, context: Context) -> Outputs | None:
    # 优先使用 cover_image，其次使用 download_cover
    cover_image = params.get('cover_image')
    if cover_image:
        return {
            "cover_image": cover_image
        }
    
    download_cover = params.get('download_cover')
    if download_cover:
        return {
            "cover_image": download_cover
        }
    
    # 如果两个参数都不存在，返回 None
    return None