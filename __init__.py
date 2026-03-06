bl_info = {
    "name": "Batch Texture Converter",
    "author": "Maylog",
    "version": (1, 0, 2),
    "blender": (4, 2, 0),
    "location": "Image Editor > Sidepanel > Converter",
    "description": "Bulk convert image formats with recursive subfolder support and Alpha splitting",
    "category": "Image",
}

import bpy
import os


class MaylogSettings(bpy.types.PropertyGroup):
    in_path: bpy.props.StringProperty(name="Source", subtype='DIR_PATH', 
        update=lambda s, c: setattr(s, "out_path", s.in_path) if not s.lock else None)
    out_path: bpy.props.StringProperty(name="Output", subtype='DIR_PATH')
    subfolders: bpy.props.BoolProperty(name="Subfolders", default=False)
    lock: bpy.props.BoolProperty(name="Lock", default=False)
    alpha: bpy.props.BoolProperty(name="Split Alpha", default=False)
    mode: bpy.props.EnumProperty(name="Mode", items=[
        ('NONE', 'None', ''), ('PIXELS', 'Pixels', ''), ('PERCENT', 'Percent', '')], default='NONE')
    w: bpy.props.IntProperty(name="W", default=1024, min=1)
    h: bpy.props.IntProperty(name="H", default=1024, min=1)
    p: bpy.props.IntProperty(name="Scale", default=100, min=1, max=1000)

    # New: batch size and aspect ratio lock
    batch_size: bpy.props.IntProperty(
        name="Images per Cycle",
        description="Number of images to process per timer cycle. Large numbers may freeze Blender.",
        default=4,
        min=1,
        soft_max=20
    )
    preserve_aspect: bpy.props.BoolProperty(
        name="Preserve Aspect Ratio",
        default=True
    )


class TEXTURE_OT_BatchConvert(bpy.types.Operator):
    bl_idname = "image.maylog_convert"
    bl_label = "Convert"
    bl_options = {'REGISTER'}
    
    _timer = None
    _files = []
    _idx = 0

    def modal(self, context, event):
        if event.type == 'ESC':
            self.report({'INFO'}, "Conversion Cancelled by User")
            return self.finish(context)

        if event.type == 'TIMER':
            for _ in range(context.scene.maylog_props.batch_size):
                if self._idx >= len(self._files):
                    return self.finish(context)
                self.process_next(context)
                self._idx += 1
            context.workspace.status_text_set(f"Converting: {(self._idx/len(self._files))*100:.1f}% (Press ESC to Cancel)")
        
        return {'PASS_THROUGH'}

    def get_ext(self, scene):
        s = scene.render.image_settings
        ext_map = {
            'BMP': ".bmp", 'PNG': ".png", 'JPEG': ".jpg", 'JPEG2000': ".jp2", 
            'TARGA': ".tga", 'TARGA_RAW': ".tga", 'TIFF': ".tif", 'DPX': ".dpx",
            'OPEN_EXR_MULTILAYER': ".exr", 'OPEN_EXR': ".exr", 'HDR': ".hdr", 
            'IRIS': ".rgb", 'WEBP': ".webp", 'AVIF': ".avif", 'JP2': ".jp2"
        }
        return ext_map.get(s.file_format, ".png")

    def process_next(self, context):
        p, s = context.scene.maylog_props, context.scene.render.image_settings
        path, f = self._files[self._idx]
        name, ext = os.path.splitext(f)
        t_dir = os.path.dirname(path)
        if p.lock:
            rel = os.path.relpath(t_dir, bpy.path.abspath(p.in_path))
            t_dir = os.path.normpath(os.path.join(bpy.path.abspath(p.out_path), rel))
        out_p = os.path.join(t_dir, f"converted_{ext[1:].lower()}")
        os.makedirs(out_p, exist_ok=True)
        try:
            img = bpy.data.images.load(path)

            # Resize with optional aspect ratio lock (only affects PIXELS mode)
            if p.mode != 'NONE':
                ow, oh = img.size
                if p.mode == 'PIXELS':
                    if p.preserve_aspect and ow > 0 and oh > 0:
                        scale = min(p.w / ow, p.h / oh)
                        tw = int(ow * scale)
                        th = int(oh * scale)
                    else:
                        tw, th = p.w, p.h
                elif p.mode == 'PERCENT':
                    fac = p.p / 100.0
                    tw = int(ow * fac)
                    th = int(oh * fac)
                if tw > 0 and th > 0:
                    img.scale(tw, th)

            base = os.path.join(out_p, name)
            t_ext = self.get_ext(context.scene)
            if p.alpha and img.channels == 4 and s.file_format in {'JPEG', 'WEBP', 'AVIF', 'JP2'}:
                self.save_alpha(img, base, context.scene, t_ext)
                s.color_mode = 'RGB'
            img.save_render(filepath=base + t_ext, scene=context.scene)
            bpy.data.images.remove(img)
        except: pass

    def save_alpha(self, img, base, scene, ext):
        w, h = img.size
        pix = list(img.pixels)
        a_data = []
        for i in range(0, len(pix), 4):
            a = pix[i + 3]
            a_data.extend([a, a, a, 1.0])
        a_img = bpy.data.images.new("TEMP_A", width=w, height=h)
        a_img.pixels = a_data
        old = scene.render.image_settings.color_mode
        scene.render.image_settings.color_mode = 'RGB'
        a_img.update()
        a_img.save_render(filepath=f"{base}_alpha{ext}", scene=scene)
        scene.render.image_settings.color_mode = old
        bpy.data.images.remove(a_img)

    def execute(self, context):
        if context.scene.render.image_settings.file_format in {'FFMPEG', 'AVI_JPEG', 'AVI_RAW'}:
            self.report({'ERROR'}, "Video formats not supported")
            return {'CANCELLED'}
        p = context.scene.maylog_props
        src = bpy.path.abspath(p.in_path)
        if not os.path.isdir(src): return {'CANCELLED'}
        valid = ('.jpg', '.jpeg', '.png', '.tga', '.tif', '.tiff', '.webp', '.bmp', '.exr', '.hdr', '.jp2')
        self._files = []
        if p.subfolders:
            for r, d, fs in os.walk(src):
                for f in fs:
                    if f.lower().endswith(valid): self._files.append((os.path.join(r, f), f))
        else:
            for f in os.listdir(src):
                if f.lower().endswith(valid): self._files.append((os.path.join(src, f), f))
        if not self._files: return {'FINISHED'}
        self._idx = 0
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self, context):
        context.window_manager.event_timer_remove(self._timer)
        context.workspace.status_text_set(None)
        return {'FINISHED'}


class TEXTURE_PT_Maylog(bpy.types.Panel):
    bl_label = "Batch Texture Converter"
    bl_idname = "TEXTURE_PT_Maylog"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Converter"

    def draw(self, context):
        layout = self.layout
        p, s = context.scene.maylog_props, context.scene.render.image_settings
        is_video = s.file_format in {'FFMPEG', 'AVI_JPEG', 'AVI_RAW'}

        c = layout.column()
        c.scale_y = 2.0
        c.active = not is_video
        c.operator("image.maylog_convert", icon='PLAY', text="Run Batch Conversion")
        if is_video:
            col = layout.column()
            col.alert = True
            col.label(text="Video formats NOT supported", icon='ERROR')

        b = layout.box()
        b.label(text="Path", icon='FILE_FOLDER')
        b.prop(p, "in_path")
        b.prop(p, "subfolders")
        r = b.row(align=True)
        r.prop(p, "out_path")
        r.prop(p, "lock", text="", icon='LOCKED' if p.lock else 'UNLOCKED')

        b = layout.box()
        b.label(text="Format Configuration", icon='IMAGE_DATA')
        b.template_image_settings(s, color_management=True)

        b = layout.box()
        b.label(text="Resize", icon='FULLSCREEN_ENTER')
        col = b.column(align=True)
        col.use_property_split = True
        col.prop(p, "mode", text="Mode")
        if p.mode == 'PIXELS':
            r = col.row(align=True)
            r.prop(p, "w")
            r.prop(p, "h")
            col.prop(p, "preserve_aspect")
        elif p.mode == 'PERCENT':
            r = col.row(align=True)
            r.prop(p, "p", text="Scale")
            r.label(text="%")

        b = layout.box()
        b.label(text="Batch Processing", icon='TIME')
        col = b.column(align=True)
        col.use_property_split = True
        col.prop(p, "batch_size")
        col.label(text="Large numbers may freeze Blender.", icon='ERROR')

        b = layout.box()
        b.label(text="Alpha", icon='IMAGE_RGB_ALPHA')
        if s.file_format in {'JPEG', 'WEBP', 'AVIF', 'JP2'}:
            col = b.column(align=True)
            col.alert = True
            col.label(text="Format doesn't support Alpha well", icon='ERROR')
            b.prop(p, "alpha")
        else:
            b.label(text="Native support"); b.active = False


classes = (MaylogSettings, TEXTURE_OT_BatchConvert, TEXTURE_PT_Maylog)


def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.maylog_props = bpy.props.PointerProperty(type=MaylogSettings)


def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    del bpy.types.Scene.maylog_props


if __name__ == "__main__":
    register()