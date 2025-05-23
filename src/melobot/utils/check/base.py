from __future__ import annotations

from abc import abstractmethod

from typing_extensions import Any, Callable, Coroutine, Generic, assert_never

from ...adapter.model import Event, EventT
from ...typ._enum import LogicMode
from ...typ.base import SyncOrAsyncCallable
from ...typ.cls import BetterABC
from ...utils.base import to_async


class Checker(Generic[EventT], BetterABC):
    """检查器基类"""

    def __init__(self, fail_cb: SyncOrAsyncCallable[[], None] | None = None) -> None:
        super().__init__()
        self.fail_cb = to_async(fail_cb) if fail_cb is not None else None

    def __and__(self, other: Checker) -> WrappedChecker:
        if not isinstance(other, Checker):
            return NotImplemented
        return WrappedChecker(LogicMode.AND, self, other)

    def __or__(self, other: Checker) -> WrappedChecker:
        if not isinstance(other, Checker):
            return NotImplemented
        return WrappedChecker(LogicMode.OR, self, other)

    def __invert__(self) -> WrappedChecker:
        return WrappedChecker(LogicMode.NOT, self)

    def __xor__(self, other: Checker) -> WrappedChecker:
        if not isinstance(other, Checker):
            return NotImplemented
        return WrappedChecker(LogicMode.XOR, self, other)

    @abstractmethod
    async def check(self, event: EventT) -> bool:
        """检查器检查方法

        任何检查器应该实现此抽象方法。

        :param event: 给定的事件
        :return: 检查是否通过
        """
        raise NotImplementedError

    @staticmethod
    def new(func: SyncOrAsyncCallable[[EventT], bool]) -> Checker[EventT]:
        """从可调用对象创建检查器

        :param func: 可调用对象
        :return: 检查器对象
        """
        return _CustomChecker[EventT](func)


class _CustomChecker(Checker[EventT]):
    def __init__(self, func: SyncOrAsyncCallable[[EventT], bool]) -> None:
        super().__init__()
        self.func = to_async(func)

    async def check(self, event: EventT) -> bool:
        return await self.func(event)


class WrappedChecker(Checker[EventT]):
    """合并检查器

    在两个 :class:`Checker` 对象间使用 | & ^ ~ 运算符即可返回合并检查器。
    """

    def __init__(
        self,
        mode: LogicMode,
        checker1: Checker,
        checker2: Checker | None = None,
    ) -> None:
        """初始化一个合并检查器

        :param mode: 合并检查的逻辑模式
        :param checker1: 检查器1
        :param checker2: 检查器2
        """
        super().__init__()
        self.mode = mode
        self.c1 = checker1
        self.c2 = checker2

    def set_fail_cb(self, fail_cb: SyncOrAsyncCallable[[], None] | None) -> None:
        self.fail_cb: Callable[[], Coroutine[Any, Any, None]] | None = (
            to_async(fail_cb) if fail_cb is not None else None
        )

    async def check(self, event: EventT) -> bool:
        match self.mode:
            case LogicMode.AND:
                status = await self.c1.check(event) and await self.c2.check(event)  # type: ignore[union-attr]
            case LogicMode.OR:
                status = await self.c1.check(event) or await self.c2.check(event)  # type: ignore[union-attr]
            case LogicMode.NOT:
                status = not await self.c1.check(event)
            case LogicMode.XOR:
                status = await self.c1.check(event) ^ await self.c2.check(event)  # type: ignore[union-attr]
            case _:
                assert_never(f"无效的逻辑模式 {self.mode}")

        if not status and self.fail_cb is not None:
            await self.fail_cb()
        return status


def checker_join(*checkers: Checker | None | Callable[[Event], bool]) -> Checker:
    """合并检查器

    相比于使用 | & ^ ~ 运算符，此函数可以接受一个检查器序列，并返回一个合并检查器。
    检查器序列可以为检查器对象，检查函数或空值

    :return: 合并后的检查器对象
    """
    checker: Checker | None = None
    for c in checkers:
        if c is None:
            continue
        if isinstance(c, Checker):
            checker = checker & c if checker else c
        else:
            checker = checker & Checker.new(c) if checker else Checker.new(c)

    if checker is None:
        raise ValueError("检查器序列不能全为空")
    return checker
