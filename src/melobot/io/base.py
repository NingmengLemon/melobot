import time
from dataclasses import dataclass, field
from enum import Enum
from types import TracebackType
from typing import Any, Generic

from typing_extensions import LiteralString, Self, TypeVar

from .._hook import Hookable
from ..typ import BetterABC, abstractmethod
from ..utils import get_id


@dataclass
class _Packet:
    time: float = field(default_factory=lambda: time.time_ns() / 1e9)
    id: str = field(default_factory=get_id)
    protocol: LiteralString | None = None
    data: Any = None


@dataclass
class InPacket(_Packet):
    """输入包基类（数据类）

    :ivar float time: 时间戳
    :ivar str id: id 标识
    :ivar typing.LiteralString | None protocol: 遵循的协议
    :ivar Any data: 附加的数据
    """


@dataclass
class OutPacket(_Packet):
    """输出包基类（数据类）

    :ivar float time: 时间戳
    :ivar str id: id 标识
    :ivar typing.LiteralString | None protocol: 遵循的协议
    :ivar Any data: 附加的数据
    """


@dataclass
class EchoPacket(_Packet):
    """回应包基类（数据类）

    :ivar float time: 时间戳
    :ivar str id: id 标识
    :ivar typing.LiteralString | None protocol: 遵循的协议
    :ivar Any data: 附加的数据
    :ivar bool ok: 回应是否成功
    :ivar int status: 回应状态码
    :ivar str prompt: 提示语
    :ivar bool noecho: 是否并无回应产生
    """

    ok: bool = True
    status: int = 0
    prompt: str = ""
    noecho: bool = False


InPacketT = TypeVar("InPacketT", bound=InPacket)
OutPacketT = TypeVar("OutPacketT", bound=OutPacket)
EchoPacketT = TypeVar("EchoPacketT", bound=EchoPacket)


class SourceLifeSpan(Enum):
    """源生命周期阶段的枚举"""

    STARTED = "sta"
    RESTARTED = "res"
    STOPPED = "sto"


class AbstractSource(BetterABC, Hookable[SourceLifeSpan]):
    """抽象源基类"""

    def __init__(self, protocol: LiteralString) -> None:
        Hookable.__init__(
            self, SourceLifeSpan, tag=f"{protocol}/{self.__class__.__name__}"
        )

        self.protocol = protocol

    @abstractmethod
    async def open(self) -> None:
        """源打开方法"""
        raise NotImplementedError

    @abstractmethod
    def opened(self) -> bool:
        """源是否已打开"""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """源关闭方法"""
        raise NotImplementedError

    async def __aenter__(self) -> Self:
        if self.opened():
            return self

        await self.open()
        await self._hook_bus.emit(SourceLifeSpan.STARTED)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if not self.opened():
            return None

        try:
            await self.close()
        finally:
            await self._hook_bus.emit(SourceLifeSpan.STOPPED, True)
        return None


class AbstractInSource(AbstractSource, BetterABC, Generic[InPacketT]):
    """抽象输入源基类"""

    @abstractmethod
    async def open(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def opened(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def input(self) -> InPacketT:
        """源输入方法

        :return: 返回 :class:`.InPacket` 对象
        """
        raise NotImplementedError


InSourceT = TypeVar("InSourceT", bound=AbstractInSource)


class AbstractOutSource(AbstractSource, BetterABC, Generic[OutPacketT, EchoPacketT]):
    """抽象输出源基类"""

    @abstractmethod
    async def open(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def opened(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def output(self, packet: OutPacketT) -> EchoPacketT:
        """源输出方法

        :return: 返回 :class:`.OutPacket` 对象
        """
        raise NotImplementedError


OutSourceT = TypeVar("OutSourceT", bound=AbstractOutSource)

InOrOutSourceT = TypeVar("InOrOutSourceT", bound=AbstractInSource | AbstractOutSource)


class AbstractIOSource(
    AbstractInSource[InPacketT], AbstractOutSource[OutPacketT, EchoPacketT], BetterABC
):
    """抽象输入输出源基类"""

    @abstractmethod
    async def open(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def opened(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def input(self) -> InPacketT:
        raise NotImplementedError

    @abstractmethod
    async def output(self, packet: OutPacketT) -> EchoPacketT:
        raise NotImplementedError


IOSourceT = TypeVar("IOSourceT", bound=AbstractIOSource)
