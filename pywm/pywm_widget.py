from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Generic

from abc import abstractmethod

# Python imports are great
if TYPE_CHECKING:
    from .pywm import PyWM, PyWMOutput, ViewT
    PyWMT = TypeVar('PyWMT', bound=PyWM)
else:
    PyWMT = TypeVar('PyWMT')


class PyWMWidgetDownstreamState:
    def __init__(self, z_index: int=0, box: tuple[float, float, float, float]=(0, 0, 0, 0), mask: tuple[float, float, float, float]=(-1, -1, -1, -1), opacity: float=1., lock_enabled: bool=True, workspace: Optional[tuple[float, float, float, float]]=None, primitive: Optional[str]=None) -> None:
        self.z_index = int(z_index)
        self.box = (float(box[0]), float(box[1]), float(box[2]), float(box[3]))
        self.mask = (float(mask[0]), float(mask[1]), float(mask[2]), float(mask[3]))
        self.opacity = opacity
        self.lock_enabled=lock_enabled
        self.workspace = workspace
        self.primitive = primitive

    def copy(self) -> PyWMWidgetDownstreamState:
        return PyWMWidgetDownstreamState(self.z_index, self.box, self.mask, self.opacity, self.lock_enabled, self.workspace)

    def get(self, root: PyWM[ViewT], output: Optional[PyWMOutput], pixels: Optional[tuple[int, int, int, bytes]], primitive: Optional[tuple[str, list[int], list[float]]]) -> tuple[bool, tuple[float, float, float, float], tuple[float, float, float, float], int, float, int, tuple[float, float, float, float], Optional[tuple[int, int, int, bytes]], Optional[tuple[str, list[int], list[float]]]]:
        return (
            self.lock_enabled,
            root.round(*self.box, wh_logical=False),
            self.mask,
            output._key if output is not None else -1,
            self.opacity,
            self.z_index,
            root.round(*self.workspace, wh_logical=False) if self.workspace is not None else (0, 0, -1, -1),
            pixels,
            primitive
        )

class PyWMWidget(Generic[PyWMT]):
    def __init__(self, wm: PyWMT, output: Optional[PyWMOutput]) -> None:
        self._handle = -1

        self.wm = wm
        self.output = output

        self._down_state = PyWMWidgetDownstreamState(0, (0, 0, 0, 0))
        self._damaged = True

        """
        (stride, width, height, data)
        """
        self._pending_pixels: Optional[tuple[int, int, int, bytes]] = None

        self._pending_primitive: Optional[tuple[str, list[int], list[float]]] = None

    def _update(self) -> tuple[bool, tuple[float, float, float, float], tuple[float, float, float, float], int, float, int, tuple[float, float, float, float], Optional[tuple[int, int, int, bytes]], Optional[tuple[str, list[int], list[float]]]]:
        if self._damaged:
            self._damaged = False
            self._down_state = self.process()
        pixels = self._pending_pixels
        primitive = self._pending_primitive
        self._pending_pixels = None
        self._pending_primitive = None
        return self._down_state.get(self.wm, self.output, pixels, primitive)

    def damage(self) -> None:
        self._damaged = True

    def destroy(self) -> None:
        self.wm.widget_destroy(self)

    def set_pixels(self, stride: int, width: int, height: int, data: bytes) -> None:
        self._pending_pixels = (stride, width, height, data)

    def set_primitive(self, name: str, params_int: list[int], params_float: list[float]) -> None:
        self._pending_primitive = name, params_int, params_float

    @abstractmethod
    def process(self) -> PyWMWidgetDownstreamState:
        """
        return next down_state based on whatever state the implementation uses
        """
        pass
