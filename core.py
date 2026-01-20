# Windows控制台窗口控制器，通过user32.dll操作窗口

import ctypes
import sys


class ConsoleWindowController:
    SW_MINIMIZE = 6
    SW_RESTORE = 9
    SWP_SHOWWINDOW = 0x0040
    SWP_NOACTIVATE = 0x0010
    GWLP_EXSTYLE = -20
    WS_EX_LAYERED = 0x80000
    LWA_ALPHA = 0x02

    ENUM_WINDOWS_PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def __init__(self):
        self.hwnd = None
        self._initialized = False
        self._layered_set = False
        if sys.platform != 'win32':
            return
        try:
            self.user32 = ctypes.WinDLL('user32', use_last_error=True)
            self._initialized = True
        except:
            pass

    def _set_hwnd(self, hwnd) -> bool:
        self.hwnd = hwnd
        self._layered_set = False
        return True

    # 查找控制台窗口，优先匹配Windows Terminal，其次传统控制台
    def find_console(self) -> bool:
        if not self._initialized:
            return False
        found_windows = []

        def enum_callback(hwnd, lparam):
            if self.user32.IsWindowVisible(hwnd):
                title = self._get_window_title(hwnd)
                classname = self._get_window_class(hwnd)
                if title or classname:
                    if ('blender' in title.lower() or 'console' in title.lower() or 'consolewindowclass' in classname.lower()):
                        found_windows.append((hwnd, classname, title))
            return True

        self.user32.EnumWindows(self.ENUM_WINDOWS_PROC(enum_callback), 0)

        for hwnd, cls, title in found_windows:
            if title.lower().startswith('blender') and 'cascadia_hosting_window_class' in cls.lower():
                return self._set_hwnd(hwnd)

        for hwnd, cls, title in found_windows:
            if 'consolewindowclass' in cls.lower():
                return self._set_hwnd(hwnd)

        for hwnd, cls, title in found_windows:
            if ('cascadia_hosting_window_class' in cls.lower() and 'blender' in title.lower() and '管理员' not in title and 'administrator' not in title.lower()):
                return self._set_hwnd(hwnd)

        return False

    def _get_window_title(self, hwnd) -> str:
        try:
            length = self.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                self.user32.GetWindowTextW(hwnd, buffer, length + 1)
                return buffer.value
        except:
            pass
        return ""

    def _get_window_class(self, hwnd) -> str:
        try:
            buffer = ctypes.create_unicode_buffer(256)
            self.user32.GetClassNameW(hwnd, buffer, 256)
            return buffer.value
        except:
            pass
        return ""

    def set_position(self, x: int, y: int, width: int, height: int, topmost: bool = True) -> bool:
        if not self._initialized or not self.hwnd:
            return False
        hwnd_param = ctypes.c_void_p(self.hwnd)
        if self.user32.IsIconic(self.hwnd):
            self.user32.ShowWindow(hwnd_param, self.SW_RESTORE)
        insert_after = ctypes.c_void_p(-1) if topmost else ctypes.c_void_p(-2)
        result = self.user32.SetWindowPos(hwnd_param, insert_after, x, y, width, height, self.SWP_SHOWWINDOW)
        if topmost:
            self.user32.BringWindowToTop(hwnd_param)
            self.user32.SetForegroundWindow(hwnd_param)
        return bool(result)

    def is_window_valid(self) -> bool:
        if not self._initialized or not self.hwnd:
            return False
        return bool(self.user32.IsWindow(self.hwnd))

    def set_position_fast(self, x: int, y: int, width: int, height: int, topmost: bool = True) -> bool:
        if not self._initialized or not self.hwnd:
            return False
        insert_after = ctypes.c_void_p(-1) if topmost else ctypes.c_void_p(-2)
        hwnd_param = ctypes.c_void_p(self.hwnd)
        flags = self.SWP_SHOWWINDOW | self.SWP_NOACTIVATE
        return bool(self.user32.SetWindowPos(hwnd_param, insert_after, x, y, width, height, flags))

    def minimize(self) -> bool:
        if not self._initialized or not self.hwnd:
            return False
        hwnd_param = ctypes.c_void_p(self.hwnd)
        return bool(self.user32.ShowWindow(hwnd_param, self.SW_MINIMIZE))

    def restore(self) -> bool:
        if not self._initialized or not self.hwnd:
            return False
        hwnd_param = ctypes.c_void_p(self.hwnd)
        return bool(self.user32.ShowWindow(hwnd_param, self.SW_RESTORE))

    def is_minimized(self) -> bool:
        if not self._initialized or not self.hwnd:
            return False
        return bool(self.user32.IsIconic(self.hwnd))

    def focus_blender(self) -> bool:
        if not self._initialized:
            return False
        blender_hwnd = self.find_blender_window()
        if blender_hwnd:
            hwnd_param = ctypes.c_void_p(blender_hwnd)
            self.user32.SetForegroundWindow(hwnd_param)
            return True
        return False

    # 设置窗口透明度，需要先启用WS_EX_LAYERED样式
    def set_opacity(self, opacity: int) -> bool:
        if not self._initialized or not self.hwnd:
            return False
        hwnd_param = ctypes.c_void_p(self.hwnd)
        if not self._layered_set:
            style = self.user32.GetWindowLongPtrW(hwnd_param, self.GWLP_EXSTYLE)
            self.user32.SetWindowLongPtrW(hwnd_param, self.GWLP_EXSTYLE, style | self.WS_EX_LAYERED)
            self._layered_set = True
        alpha = max(0, min(255, int(opacity * 255 / 100)))
        return bool(self.user32.SetLayeredWindowAttributes(hwnd_param, 0, alpha, self.LWA_ALPHA))

    def find_blender_window(self):
        if not self._initialized:
            return None
        blender_hwnd = None

        def enum_callback(hwnd, lparam):
            nonlocal blender_hwnd
            classname = self._get_window_class(hwnd)
            if classname == 'GHOST_WindowClass':
                blender_hwnd = hwnd
                return False
            return True

        self.user32.EnumWindows(self.ENUM_WINDOWS_PROC(enum_callback), 0)
        return blender_hwnd


_console_controller = None

def get_controller() -> ConsoleWindowController:
    global _console_controller
    if _console_controller is None:
        _console_controller = ConsoleWindowController()
    return _console_controller

def reset_controller():
    global _console_controller
    _console_controller = None
