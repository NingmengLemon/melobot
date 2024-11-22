from os import PathLike
from typing import Sequence

from ..ctx import EventBuildInfoCtx
from .content import Content
from .model import ActionHandle, Event

_CTX = EventBuildInfoCtx()


async def send_text(text: str) -> tuple[ActionHandle, ...]:
    """包装对当前上下文中适配器的 :meth:`~melobot.adapter.Adapter.send_text` 调用

    函数参数和返回值参考原方法
    """
    return await _CTX.get().adapter.__send_text__(text)


async def send_media(
    name: str,
    raw: bytes | None = None,
    url: str | None = None,
    mimetype: str | None = None,
) -> tuple[ActionHandle, ...]:
    """包装对当前上下文中适配器的 :meth:`~melobot.adapter.Adapter.send_media` 调用

    函数参数和返回值参考原方法
    """
    return await _CTX.get().adapter.__send_media__(name, raw, url, mimetype)


async def send_image(
    name: str,
    raw: bytes | None = None,
    url: str | None = None,
    mimetype: str | None = None,
) -> tuple[ActionHandle, ...]:
    """包装对当前上下文中适配器的 :meth:`~melobot.adapter.Adapter.send_image` 调用

    函数参数和返回值参考原方法
    """
    return await _CTX.get().adapter.__send_image__(name, raw, url, mimetype)


async def send_audio(
    name: str,
    raw: bytes | None = None,
    url: str | None = None,
    mimetype: str | None = None,
) -> tuple[ActionHandle, ...]:
    """包装对当前上下文中适配器的 :meth:`~melobot.adapter.Adapter.send_audio` 调用

    函数参数和返回值参考原方法
    """
    return await _CTX.get().adapter.__send_audio__(name, raw, url, mimetype)


async def send_voice(
    name: str,
    raw: bytes | None = None,
    url: str | None = None,
    mimetype: str | None = None,
) -> tuple[ActionHandle, ...]:
    """包装对当前上下文中适配器的 :meth:`~melobot.adapter.Adapter.send_voice` 调用

    函数参数和返回值参考原方法
    """
    return await _CTX.get().adapter.__send_voice__(name, raw, url, mimetype)


async def send_video(
    name: str,
    raw: bytes | None = None,
    url: str | None = None,
    mimetype: str | None = None,
) -> tuple[ActionHandle, ...]:
    """包装对当前上下文中适配器的 :meth:`~melobot.adapter.Adapter.send_video` 调用

    函数参数和返回值参考原方法
    """
    return await _CTX.get().adapter.__send_video__(name, raw, url, mimetype)


async def send_file(name: str, path: str | PathLike[str]) -> tuple[ActionHandle, ...]:
    """包装对当前上下文中适配器的 :meth:`~melobot.adapter.Adapter.send_file` 调用

    函数参数和返回值参考原方法
    """
    return await _CTX.get().adapter.__send_file__(name, path)


async def send_refer(
    event: Event, contents: Sequence[Content] | None = None
) -> tuple[ActionHandle, ...]:
    """包装对当前上下文中适配器的 :meth:`~melobot.adapter.Adapter.send_refer` 调用

    函数参数和返回值参考原方法
    """
    return await _CTX.get().adapter.__send_refer__(event, contents)


async def send_resource(name: str, url: str) -> tuple[ActionHandle, ...]:
    """包装对当前上下文中适配器的 :meth:`~melobot.adapter.Adapter.send_resource` 调用

    函数参数和返回值参考原方法
    """
    return await _CTX.get().adapter.__send_resource__(name, url)
