Batch Texture Converter
This is a plugin designed to help you quickly and efficiently batch convert texture formats.

* UI Location: Found in the Image Editor > Sidepanel (N) > Converter tab.

* Recursive Scanning: Automatically scans and converts textures in all subfolders.

* Smart Alpha Splitting: Optional extraction of the Alpha channel into a separate grayscale map—perfect for JPEG or WebP workflows.

* Non-Blocking Workflow: Uses an asynchronous modal timer to keep the Blender interface responsive with a real-time progress bar.

* Organized Output: Automatically categorizes converted files into subfolders based on their new format.

* Compositor Batch Processing: processing images through custom Compositor Node Trees.

  * Workflow: Organize your nodes as 【 Image Input node > Your custom nodes > File Output node 】 . The addon will automatically swap images and trigger the render for each file in the batch.

  * Due to the dependency on independent node structures for the Compositor integration, this add-on requires Blender 5.0 or higher.

__Special Thanks:__

* Special thanks to  @Nezumi.blend  (BlenderArtists) for providing invaluable technical guidance and assistance during the development of the Compositor integration.
