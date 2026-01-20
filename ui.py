# UI界面和操作符定义

import bpy
from bpy.props import IntProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Panel, AddonPreferences
from .core import get_controller
from .i18n import get_text, get_language_items

_pending_toggle_prefs = None
addon_keymaps = []


def ensure_controller_ready():
    controller = get_controller()
    if not controller.hwnd or not controller.is_window_valid():
        controller.find_console()
    return controller


def apply_console_settings(controller, prefs):
    controller.set_position(prefs.pos_x, prefs.pos_y, prefs.width, prefs.height, prefs.always_on_top)
    controller.set_opacity(prefs.opacity)


def _with_console(action):
    controller = get_controller()
    if not controller.hwnd or not controller.is_window_valid():
        controller.find_console()
    if controller.hwnd:
        action(controller)


def update_console_transform(self, context):
    _with_console(lambda c: c.set_position_fast(self.pos_x, self.pos_y, self.width, self.height, self.always_on_top))


def update_console_opacity(self, context):
    _with_console(lambda c: c.set_opacity(self.opacity))


def draw_single_keymap_item(layout, km, kmi):
    col = layout.column()
    col.context_pointer_set("keymap", km)

    row = col.row(align=True)
    row.prop(kmi, "active", text="", emboss=False)
    row.prop(kmi, "show_expanded", text="", emboss=False)
    row.label(text=kmi.name if kmi.name else kmi.idname)
    row.prop(kmi, "type", text="", full_event=True)

    op = row.operator("preferences.keyitem_restore", text="", icon='LOOP_BACK')
    op.item_id = kmi.id

    if kmi.show_expanded:
        box = col.box()
        split = box.split(factor=0.4)
        sub = split.row()
        sub.prop(kmi, "idname", text="")
        sub = split.column()
        sub_row = sub.row(align=True)
        sub_row.prop(kmi, "type", text="")
        sub_row.prop(kmi, "value", text="")
        sub = box.column()
        sub_row = sub.row()
        sub_row.scale_x = 0.75
        sub_row.prop(kmi, "any", toggle=True)
        sub_row.prop(kmi, "shift_ui", toggle=True)
        sub_row.prop(kmi, "ctrl_ui", toggle=True)
        sub_row.prop(kmi, "alt_ui", toggle=True)
        sub_row.prop(kmi, "oskey_ui", toggle=True)


def draw_addon_keymaps(layout, context):
    kc = context.window_manager.keyconfigs.user
    for km, kmi in addon_keymaps:
        km_user = kc.keymaps.get(km.name)
        if km_user:
            for kmi_user in km_user.keymap_items:
                if kmi_user.idname == kmi.idname:
                    draw_single_keymap_item(layout, km_user, kmi_user)
                    break


def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Window', space_type='EMPTY')
        kmi = km.keymap_items.new('console.toggle', 'ACCENT_GRAVE', 'PRESS', ctrl=True)
        kmi.show_expanded = True
        addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


class ConsoleControlPreferences(AddonPreferences):
    bl_idname = __package__

    language: EnumProperty(
        name="Language",
        items=get_language_items,
    )
    pos_x: IntProperty(name="Position X", default=-5, min=-5000, max=8000, soft_min=-5000, soft_max=8000, update=update_console_transform)
    pos_y: IntProperty(name="Position Y", default=530, min=-500, max=5000, soft_min=0, soft_max=2160, update=update_console_transform)
    width: IntProperty(name="Width", default=575, min=50, max=7680, soft_min=50, soft_max=3840, update=update_console_transform)
    height: IntProperty(name="Height", default=360, min=50, max=4320, soft_min=50, soft_max=2160, update=update_console_transform)
    always_on_top: BoolProperty(name="Always On Top", default=True, update=update_console_transform)
    auto_open_on_startup: BoolProperty(name="Auto Open On Startup", default=True)
    opacity: IntProperty(name="Opacity", default=100, min=10, max=100, soft_min=10, soft_max=100, subtype='PERCENTAGE', update=update_console_opacity)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "language", text=get_text("Language"))
        layout.separator()
        layout.label(text=get_text("Keymap") + ":")
        box = layout.box()
        draw_addon_keymaps(box, context)


# 延迟打开控制台，等待窗口创建完成后再应用设置
def _open_console_deferred(prefs):
    global _pending_toggle_prefs
    bpy.ops.wm.console_toggle()
    _pending_toggle_prefs = prefs
    bpy.app.timers.register(_apply_after_toggle, first_interval=0.3)


def _apply_after_toggle():
    global _pending_toggle_prefs
    if _pending_toggle_prefs is None:
        return None
    controller = get_controller()
    if controller.find_console():
        apply_console_settings(controller, _pending_toggle_prefs)
        CONSOLE_OT_toggle._first_run = False
    _pending_toggle_prefs = None
    return None


class CONSOLE_OT_toggle(Operator):
    bl_idname = "console.toggle"
    bl_label = "Toggle Console"
    bl_options = {'REGISTER'}
    _first_run = True

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences

        if CONSOLE_OT_toggle._first_run:
            _open_console_deferred(prefs)
            CONSOLE_OT_toggle._first_run = False
        else:
            controller = ensure_controller_ready()
            if controller.hwnd:
                if controller.is_minimized():
                    controller.restore()
                    apply_console_settings(controller, prefs)
                else:
                    controller.minimize()
                controller.focus_blender()
            else:
                _open_console_deferred(prefs)
        return {'FINISHED'}


class CONSOLE_OT_reset_position(Operator):
    bl_idname = "console.reset_position"
    bl_label = "Reset to Default"
    bl_options = {'REGISTER'}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.pos_x = -5
        prefs.pos_y = 530
        prefs.width = 575
        prefs.height = 360
        prefs.opacity = 100
        return {'FINISHED'}


class CONSOLE_PT_control_panel(Panel):
    bl_label = "Console"
    bl_idname = "CONSOLE_PT_control_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Console"

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__package__].preferences
        col = layout.column(align=True)
        col.operator("console.toggle", text=get_text("Toggle Console"), icon='CONSOLE')
        col.separator()
        box = col.box()
        sub = box.column(align=True)
        sub.prop(prefs, "pos_x", text="X")
        sub.prop(prefs, "pos_y", text="Y")
        sub.prop(prefs, "width", text=get_text("Width"))
        sub.prop(prefs, "height", text=get_text("Height"))
        box.prop(prefs, "opacity", text=get_text("Opacity"), slider=True)
        box.prop(prefs, "always_on_top", text=get_text("Always On Top"))
        box.prop(prefs, "auto_open_on_startup", text=get_text("Auto Open On Startup"))
        col.separator()
        col.operator("console.reset_position", text=get_text("Reset to Default"), icon='LOOP_BACK')


classes = (
    ConsoleControlPreferences,
    CONSOLE_OT_toggle,
    CONSOLE_OT_reset_position,
    CONSOLE_PT_control_panel,
)
