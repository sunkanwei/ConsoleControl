# 控制台窗口控制插件 - 调整系统控制台的位置、大小、透明度等

bl_info = {
    "name": "Console Control",
    "author": "Sunkanwei",
    "version": (2, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Console",
    "description": "Control the system console window position, size, opacity and more",
    "category": "System",
}

import bpy
import sys
from ctypes import c_void_p, c_uint, c_long, WINFUNCTYPE
from .core import get_controller, reset_controller
from .ui import classes, CONSOLE_OT_toggle, register_keymaps, unregister_keymaps, apply_console_settings

# Windows事件钩子常量
EVENT_SYSTEM_MINIMIZESTART = 0x0016
EVENT_SYSTEM_MINIMIZEEND = 0x0017
WINEVENT_OUTOFCONTEXT = 0x0000

_win_event_hook = None
_win_event_callback = None
_blender_hwnd = None
_timer_registered = False
_startup_attempts = 0


# 监听Blender窗口最小化/还原事件，同步控制台状态
def _win_event_proc(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
    if hwnd != _blender_hwnd:
        return
    controller = get_controller()
    if not controller.hwnd or not controller.is_window_valid():
        return
    try:
        prefs = bpy.context.preferences.addons[__name__].preferences
    except:
        return
    if event == EVENT_SYSTEM_MINIMIZESTART:
        controller.minimize()
    elif event == EVENT_SYSTEM_MINIMIZEEND:
        controller.restore()
        apply_console_settings(controller, prefs)


def setup_window_hook():
    global _win_event_hook, _win_event_callback, _blender_hwnd
    if sys.platform != 'win32':
        return
    controller = get_controller()
    if not controller._initialized:
        return
    _blender_hwnd = controller.find_blender_window()
    if not _blender_hwnd:
        return
    WINEVENTPROC = WINFUNCTYPE(None, c_void_p, c_uint, c_void_p, c_long, c_long, c_uint, c_uint)
    _win_event_callback = WINEVENTPROC(_win_event_proc)
    _win_event_hook = controller.user32.SetWinEventHook(
        EVENT_SYSTEM_MINIMIZESTART,
        EVENT_SYSTEM_MINIMIZEEND,
        None,
        _win_event_callback,
        0,
        0,
        WINEVENT_OUTOFCONTEXT
    )


def remove_window_hook():
    global _win_event_hook, _win_event_callback, _blender_hwnd
    if _win_event_hook:
        controller = get_controller()
        if controller._initialized:
            controller.user32.UnhookWinEvent(_win_event_hook)
        _win_event_hook = None
    _win_event_callback = None
    _blender_hwnd = None


# 启动时应用控制台设置，最多重试20次
def apply_console_settings_on_startup():
    global _startup_attempts, _timer_registered
    _startup_attempts += 1
    try:
        prefs = bpy.context.preferences.addons[__name__].preferences
        if not prefs.auto_open_on_startup:
            _startup_attempts = 0
            _timer_registered = False
            return None
        controller = get_controller()
        found = controller.find_console()
        if not found:
            if _startup_attempts == 1:
                try:
                    window = bpy.context.window_manager.windows[0]
                    area = next((a for a in window.screen.areas if a.type == 'VIEW_3D'), None)
                    if area:
                        with bpy.context.temp_override(window=window, area=area):
                            bpy.ops.wm.console_toggle()
                except:
                    pass
            if _startup_attempts < 20:
                return 0.1
            else:
                _timer_registered = False
                return None
        apply_console_settings(controller, prefs)
        CONSOLE_OT_toggle._first_run = False
        _startup_attempts = 0
        _timer_registered = False
    except:
        _timer_registered = False
    return None


@bpy.app.handlers.persistent
def load_post_handler(dummy):
    global _startup_attempts, _timer_registered
    if _timer_registered:
        return
    _startup_attempts = 0
    _timer_registered = True
    bpy.app.timers.register(apply_console_settings_on_startup, first_interval=0.1)


def register():
    global _timer_registered, _startup_attempts
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()
    CONSOLE_OT_toggle._first_run = True
    if load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_post_handler)
    _startup_attempts = 0
    if not _timer_registered:
        _timer_registered = True
        bpy.app.timers.register(apply_console_settings_on_startup, first_interval=0.1)
    setup_window_hook()


def unregister():
    global _timer_registered
    _timer_registered = False
    remove_window_hook()
    unregister_keymaps()
    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    reset_controller()


if __name__ == "__main__":
    register()
