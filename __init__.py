bl_info = {
    "name": "Batch Texture Converter",
    "author": "Maylog",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "Image Editor > Sidepanel > Converter",
    "description": "Bulk convert image formats with recursive subfolder support and Alpha splitting",
    "category": "Image",
}

import bpy
import os

class TEXTURE_OT_BatchConverter(bpy.types.Operator):
    bl_idname = "image.maylog_batch_convert"
    bl_label = "Convert Textures"
    bl_options = {'REGISTER'}

    _timer = None
    _files_data = [] # List of tuples: (full_path, filename)
    _index = 0
    _in_dir = ""
    _out_dir = ""

    def modal(self, context, event):
        if event.type == 'TIMER':
            if self._index >= len(self._files_data):
                return self.finish(context)

            self.convert_next(context)
            self._index += 1
            
            progress = (self._index / len(self._files_data)) * 100
            context.workspace.status_text_set(f"Converting: {self._index}/{len(self._files_data)} ({progress:.1f}%)")

        return {'PASS_THROUGH'}

    def convert_next(self, context):
        props = context.scene.maylog_tex_props
        img_settings = context.scene.render.image_settings
        full_path, f = self._files_data[self._index]
        
        name_no_ext, orig_ext = os.path.splitext(f)
        current_dir = os.path.dirname(full_path)
        
        # Determine base output directory
        if props.lock_output:
            # If output is locked, we mirror the relative structure if possible or flat export
            rel_path = os.path.relpath(current_dir, self._in_dir)
            target_base = os.path.normpath(os.path.join(self._out_dir, rel_path))
        else:
            target_base = current_dir

        sub_folder = f"converted_{orig_ext[1:].lower()}"
        final_out_path = os.path.join(target_base, sub_folder)
        os.makedirs(final_out_path, exist_ok=True)

        try:
            img = bpy.data.images.load(full_path)
            save_path_no_ext = os.path.join(final_out_path, name_no_ext)
            
            fmt = img_settings.file_format
            if props.split_alpha and img.channels == 4 and fmt in {'JPEG', 'WEBP', 'AVIF'}:
                self.extract_alpha(img, save_path_no_ext, context.scene)
                img_settings.color_mode = 'RGB'
            
            ext_map = {'JPEG': '.jpg', 'PNG': '.png', 'TIFF': '.tif', 'TARGA': '.tga', 
                       'WEBP': '.webp', 'BMP': '.bmp', 'OPEN_EXR': '.exr', 'HDR': '.hdr', 'AVIF': '.avif'}
            target_ext = ext_map.get(fmt, ".png")
            
            img.save_render(filepath=save_path_no_ext + target_ext, scene=context.scene)
            bpy.data.images.remove(img)
        except Exception as e:
            self.report({'WARNING'}, f"Error: {f} - {str(e)}")

    def extract_alpha(self, img, base_path, scene):
        width, height = img.size
        pixels = list(img.pixels)
        alpha_data = []
        for i in range(0, len(pixels), 4):
            a = pixels[i+3]
            alpha_data.extend([a, a, a, 1.0])
        
        tmp_name = "MAYLOG_ALPHA_TEMP"
        if tmp_name in bpy.data.images: bpy.data.images.remove(bpy.data.images[tmp_name])
        alpha_img = bpy.data.images.new(tmp_name, width=width, height=height)
        alpha_img.pixels = alpha_data
        
        orig_mode = scene.render.image_settings.color_mode
        scene.render.image_settings.color_mode = 'RGB'
        alpha_img.update()
        
        ext_map = {'JPEG': '.jpg', 'PNG': '.png', 'TIFF': '.tif', 'TARGA': '.tga', 
                   'WEBP': '.webp', 'BMP': '.bmp', 'OPEN_EXR': '.exr', 'HDR': '.hdr', 'AVIF': '.avif'}
        alpha_ext = ext_map.get(scene.render.image_settings.file_format, ".jpg")
        
        alpha_img.save_render(filepath=f"{base_path}_alpha{alpha_ext}", scene=scene)
        scene.render.image_settings.color_mode = orig_mode
        bpy.data.images.remove(alpha_img)

    def execute(self, context):
        props = context.scene.maylog_tex_props
        self._in_dir = bpy.path.abspath(props.input_path)
        self._out_dir = bpy.path.abspath(props.output_path)
        
        if not os.path.isdir(self._in_dir):
            self.report({'ERROR'}, "Invalid Input Path")
            return {'CANCELLED'}

        exts = ('.jpg', '.jpeg', '.png', '.tga', '.tif', '.tiff', '.webp', '.bmp', '.exr', '.hdr')
        self._files_data = []

        if props.include_subfolders:
            for root, dirs, files in os.walk(self._in_dir):
                for f in files:
                    if f.lower().endswith(exts):
                        self._files_data.append((os.path.join(root, f), f))
        else:
            for f in os.listdir(self._in_dir):
                if f.lower().endswith(exts):
                    self._files_data.append((os.path.join(self._in_dir, f), f))
        
        if not self._files_data:
            self.report({'INFO'}, "No valid images found")
            return {'FINISHED'}

        self._index = 0
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self, context):
        context.window_manager.event_timer_remove(self._timer)
        context.workspace.status_text_set(None)
        self.report({'INFO'}, f"Processed {len(self._files_data)} images")
        return {'FINISHED'}

def update_path_sync(self, context):
    props = context.scene.maylog_tex_props
    if not props.lock_output:
        props.output_path = props.input_path

class TEXTURE_PT_MaylogPanel(bpy.types.Panel):
    bl_label = "Batch Texture Converter"
    bl_idname = "TEXTURE_PT_MaylogPanel"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Converter"

    def draw(self, context):
        layout = self.layout
        props = context.scene.maylog_tex_props
        img_settings = context.scene.render.image_settings

        layout.operator("image.maylog_batch_convert", icon='PLAY', text="Run Batch Conversion")
        layout.separator()

        box = layout.box()
        box.label(text="Path Settings", icon='FILE_FOLDER')
        box.prop(props, "input_path", text="Source")
        box.prop(props, "include_subfolders", text="Include Subfolders", icon='FILE_PARENT')
        
        row = box.row(align=True)
        row.prop(props, "output_path", text="Output")
        row.prop(props, "lock_output", text="", icon='LOCKED' if props.lock_output else 'UNLOCKED')

        box = layout.box()
        box.label(text="Format Configuration", icon='IMAGE_DATA')
        box.template_image_settings(img_settings, color_management=True)

        alpha_box = layout.box()
        alpha_box.label(text="Alpha Management", icon='IMAGE_RGB_ALPHA')
        if img_settings.file_format in {'JPEG', 'WEBP', 'AVIF'}:
            col = alpha_box.column(align=True)
            col.alert = True
            col.label(text="Poor Alpha support for this format", icon='ERROR')
            alpha_box.prop(props, "split_alpha", text="Split Alpha Map")
        else:
            alpha_box.label(text="Alpha supported natively")
            alpha_box.active = False

class MaylogBatchProperties(bpy.types.PropertyGroup):
    input_path: bpy.props.StringProperty(name="Source Path", subtype='DIR_PATH', update=update_path_sync)
    output_path: bpy.props.StringProperty(name="Output Path", subtype='DIR_PATH')
    include_subfolders: bpy.props.BoolProperty(name="Include Subfolders", default=False)
    lock_output: bpy.props.BoolProperty(name="Lock Output Path", default=False)
    split_alpha: bpy.props.BoolProperty(name="Split Alpha", default=True)

classes = (MaylogBatchProperties, TEXTURE_OT_BatchConverter, TEXTURE_PT_MaylogPanel)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.maylog_tex_props = bpy.props.PointerProperty(type=MaylogBatchProperties)

def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    del bpy.types.Scene.maylog_tex_props

if __name__ == "__main__":
    register()