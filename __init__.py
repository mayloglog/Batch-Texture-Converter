bl_info = {
    "name": "Batch Texture Converter",
    "author": "Maylog",
    "version": (1, 1, 0),
    "blender": (5, 0, 0),
    "location": "Image Editor > Sidepanel > Converter",
    "description": "Bulk convert image formats with recursive subfolder support and Alpha splitting",
    "category": "Image",
}

import bpy
import os
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import StringProperty, BoolProperty, IntProperty, EnumProperty, PointerProperty

def get_compositor_nodetrees(self, context):
    items = []
    items.append(("NONE", "-- Select Node Tree --", "Choose a compositor node tree"))
    for ng in bpy.data.node_groups:
        if ng.type == 'COMPOSITING':
            items.append((ng.name, ng.name, f"Nodes: {len(ng.nodes)}"))
    if len(items) == 1:
        items = [("NONE", "-- No Node Trees --", "Create a compositor tree first")]
    return items

class BSettings(PropertyGroup):
    in_path: StringProperty(name="Source", subtype='DIR_PATH',
        update=lambda s, c: setattr(s, "out_path", s.in_path) if not s.lock else None)
    out_path: StringProperty(name="Output", subtype='DIR_PATH')
    subfolders: BoolProperty(name="Subfolders", default=False)
    lock: BoolProperty(name="Lock", default=False)
    alpha: BoolProperty(name="Split Alpha", default=False)
    mode: EnumProperty(name="Mode", items=[
        ('NONE', 'None', ''), ('PIXELS', 'Pixels', ''), ('PERCENT', 'Percent', '')], default='NONE')
    w: IntProperty(name="W", default=1024, min=1)
    h: IntProperty(name="H", default=1024, min=1)
    p: IntProperty(name="Scale", default=100, min=1, max=1000)

    batch_size: IntProperty(
        name="Images per Cycle",
        description="Number of images per timer cycle. Large values may freeze Blender.",
        default=4,
        min=1,
        soft_max=20
    )
    preserve_aspect: BoolProperty(
        name="Preserve Aspect Ratio",
        default=True
    )

    use_compositor: BoolProperty(
        name="Use Compositor",
        description="Apply selected compositor node tree before final save",
        default=False
    )

    comp_node_tree: EnumProperty(
        name="Node Tree",
        description="Select compositor node tree",
        items=get_compositor_nodetrees
    )


class TEXTURE_OT_BatchConvert(Operator):
    bl_idname = "image.b_convert"
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
            for _ in range(context.scene.b_props.batch_size):
                if self._idx >= len(self._files):
                    return self.finish(context)
                self.process_next(context)
                self._idx += 1
            context.workspace.status_text_set(f"Converting: {(self._idx/len(self._files))*100:.1f}% (Press ESC to Cancel)")

        return {'PASS_THROUGH'}

    def get_ext(self, scene):
        s = scene.render.image_settings
        ext_map = {
            'BMP': ".bmp",
            'PNG': ".png",
            'JPEG': ".jpg",
            'JPEG2000': ".jp2",
            'TARGA': ".tga",
            'TARGA_RAW': ".tga",
            'TIFF': ".tif",
            'DPX': ".dpx",
            'OPEN_EXR_MULTILAYER': ".exr",
            'OPEN_EXR': ".exr",
            'HDR': ".hdr",
            'IRIS': ".rgb",
            'WEBP': ".webp",
            'AVIF': ".avif",
            'JP2': ".jp2"
        }
        return ext_map.get(s.file_format, ".png")

    def process_next(self, context):
        p = context.scene.b_props
        s = context.scene.render.image_settings
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
            compositor_used = False

            if p.use_compositor and p.comp_node_tree != "NONE":
                node_tree = bpy.data.node_groups.get(p.comp_node_tree)
                if node_tree and node_tree.type == 'COMPOSITING':
                    context.scene.compositing_node_group = node_tree

                    img_nodes = [n for n in node_tree.nodes if n.type == 'IMAGE']
                    fout_nodes = [n for n in node_tree.nodes if n.type == 'OUTPUT_FILE']

                    if img_nodes and fout_nodes:
                        img_node = img_nodes[0]
                        fout_node = fout_nodes[0]

                        img_node.image = img
                        
                        fout_node.directory = out_p
                        fout_node.file_name = name
                        
                        f_set = fout_node.format
                        f_set.media_type = 'IMAGE'
                        
                        try:
                            f_set.file_format = s.file_format
                            f_set.color_mode = s.color_mode
                            f_set.color_depth = s.color_depth
                            if s.file_format in {'JPEG', 'WEBP', 'PNG'}:
                                f_set.compression = s.compression
                                f_set.quality = s.quality
                            if hasattr(s, "exr_codec"):
                                f_set.exr_codec = s.exr_codec
                        except:
                            pass

                        bpy.ops.render.render(write_still=True)

                        bpy.data.images.remove(img)
                        compositor_used = True

            if not compositor_used:
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

                if p.alpha and img.channels == 4:
                    if s.file_format in {'JPEG', 'WEBP'}:
                        self.save_alpha(img, base, context.scene, t_ext)
                        s.color_mode = 'RGB'
                    elif s.file_format in {'PNG', 'TARGA', 'TIFF', 'OPEN_EXR', 'BMP'}:
                        img.save_render(filepath=base + t_ext, scene=context.scene)
                        self.save_alpha(img, base, context.scene, t_ext)
                        bpy.data.images.remove(img)
                        return

                img.save_render(filepath=base + t_ext, scene=context.scene)
                bpy.data.images.remove(img)

        except Exception as e:
            print(f"Error processing {f}: {e}")

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
        p = context.scene.b_props
        if p.use_compositor:
            p.batch_size = 1

        if context.scene.render.image_settings.file_format in {'FFMPEG', 'AVI_JPEG', 'AVI_RAW'}:
            self.report({'ERROR'}, "Video formats not supported")
            return {'CANCELLED'}

        src = bpy.path.abspath(p.in_path)
        if not os.path.isdir(src):
            return {'CANCELLED'}

        valid = ('.jpg', '.jpeg', '.png', '.tga', '.tif', '.tiff', '.webp', '.bmp', '.exr', '.hdr', '.jp2', '.dds', '.DDS')
        self._files = []
        if p.subfolders:
            for r, d, fs in os.walk(src):
                for f in fs:
                    if f.lower().endswith(valid):
                        self._files.append((os.path.join(r, f), f))
        else:
            for f in os.listdir(src):
                if f.lower().endswith(valid):
                    self._files.append((os.path.join(src, f), f))

        if not self._files:
            return {'FINISHED'}

        self._idx = 0
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self, context):
        context.window_manager.event_timer_remove(self._timer)
        context.workspace.status_text_set(None)
        return {'FINISHED'}


class TEXTURE_PT_B(Panel):
    bl_label = "Batch Texture Converter"
    bl_idname = "TEXTURE_PT_B"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Converter"

    def draw(self, context):
        layout = self.layout
        p, s = context.scene.b_props, context.scene.render.image_settings
        is_video = s.file_format in {'FFMPEG', 'AVI_JPEG', 'AVI_RAW'}

        c = layout.column()
        c.scale_y = 2.0
        c.active = not is_video
        c.operator("image.b_convert", icon='PLAY', text="Run Batch Conversion")
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
        row = col.row()
        row.enabled = not p.use_compositor
        row.prop(p, "batch_size")
        col.label(text="Large numbers may freeze Blender.", icon='ERROR')

        b = layout.box()
        b.label(text="Alpha", icon='IMAGE_RGB_ALPHA')
        
        b.prop(p, "alpha")
        
        # Red warning for formats with poor alpha support
        if s.file_format in {'BMP', 'JPEG', 'WEBP'}:
            col = b.column(align=True)
            col.alert = True
            col.label(text="This format has poor alpha support.", icon='ERROR')
            col.label(text="Splitting alpha is recommended.")

        layout.separator(factor=2)
        b = layout.box()
        b.label(text="Compositor Processing", icon='NODETREE')
        col = b.column(align=True)
        col.prop(p, "use_compositor")
        
        if p.use_compositor:
            info_col = col.column(align=True)
            info_col.scale_y = 0.8
            info_col.label(text="Process via:")
            info_col.label(text="Image node > your nodes > File Output node.")
            info_col.label(text="Must be set up correctly, otherwise skipped.")
            info_col.separator()
            
            col.prop(p, "comp_node_tree", text="")
            
            valid_trees = [ng.name for ng in bpy.data.node_groups if ng.type == 'COMPOSITING']
            if p.comp_node_tree != "NONE" and p.comp_node_tree not in valid_trees:
                p.comp_node_tree = "NONE"
        else:
            col.label(text="Enable to use compositor node trees", icon='INFO')


classes = (
    BSettings,
    TEXTURE_OT_BatchConvert,
    TEXTURE_PT_B,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.b_props = PointerProperty(type=BSettings)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.b_props


if __name__ == "__main__":
    register()