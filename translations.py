# translations.py
# Batch Texture Converter 插件翻译文件

translations_dict = {
    "zh_HANS": {
        # bl_info 中的描述
        ("*", "Bulk convert image formats with recursive subfolder support and Alpha splitting"): "批量转换图像格式，支持递归子文件夹和 Alpha 拆分",
        
        # BSettings 属性
        ("*", "Source"): "源路径",
        ("*", "Output"): "输出路径",
        ("*", "Subfolders"): "子文件夹",
        ("*", "Lock"): "锁定",
        ("*", "Split Alpha"): "拆分 Alpha",
        ("*", "Mode"): "模式",
        ("*", "None"): "无",
        ("*", "Pixels"): "像素",
        ("*", "Percent"): "百分比",
        ("*", "W"): "宽",
        ("*", "H"): "高",
        ("*", "Scale"): "缩放",
        ("*", "Images per Cycle"): "每周期处理图像数",
        ("*", "Number of images per timer cycle. Large values may freeze Blender."): "每个计时周期处理的图像数量。数值过大可能导致 Blender 卡顿。",
        ("*", "Preserve Aspect Ratio"): "保持宽高比",
        ("*", "Use Compositor"): "使用合成器",
        ("*", "Apply selected compositor node tree before final save"): "在最终保存前应用选中的合成器节点树",
        ("*", "Node Tree"): "节点树",
        ("*", "Select compositor node tree"): "选择合成器节点树",
        ("*", "-- Select Node Tree --"): "-- 选择节点树 --",
        ("*", "Choose a compositor node tree"): "选择一个合成器节点树",
        ("*", "-- No Node Trees --"): "-- 无节点树 --",
        ("*", "Create a compositor tree first"): "请先创建一个合成器节点树",
        ("*", "Nodes: {}"): "节点数：{}",
        
        # 操作类 (bl_label)
        ("*", "Convert"): "转换",
        
        # 面板标题
        ("*", "Batch Texture Converter"): "批量纹理转换器",
        ("*", "Path"): "路径",
        ("*", "Format Configuration"): "格式配置",
        ("*", "Resize"): "调整大小",
        ("*", "Batch Processing"): "批量处理",
        ("*", "Large numbers may freeze Blender."): "数值过大可能导致 Blender 卡顿。",
        ("*", "Alpha"): "Alpha",
        ("*", "This format has poor alpha support."): "此格式对 Alpha 通道支持不佳。",
        ("*", "Splitting alpha is recommended."): "建议拆分 Alpha 通道。",
        ("*", "Compositor Processing"): "合成器处理",
        ("*", "Process via:"): "处理方式：",
        ("*", "Image node > your nodes > File Output node."): "图像节点 > 您的节点 > 文件输出节点。",
        ("*", "Must be set up correctly, otherwise skipped."): "必须正确设置，否则将被跳过。",
        ("*", "Enable to use compositor node trees"): "启用后可使用合成器节点树",
        
        # 按钮文本
        ("*", "Run Batch Conversion"): "运行批量转换",
        
        # 报告信息
        ("*", "Conversion Cancelled by User"): "用户取消转换",
        ("*", "Converting: {:.1f}% (Press ESC to Cancel)"): "正在转换：{:.1f}%（按 ESC 取消）",
        ("*", "Video formats not supported"): "不支持视频格式",
        ("*", "Video formats NOT supported"): "不支持视频格式",
    },
    "zh_HANT": {
        # bl_info 中的描述
        ("*", "Bulk convert image formats with recursive subfolder support and Alpha splitting"): "批量轉換圖像格式，支援遞迴子資料夾和 Alpha 拆分",
        
        # BSettings 屬性
        ("*", "Source"): "來源路徑",
        ("*", "Output"): "輸出路徑",
        ("*", "Subfolders"): "子資料夾",
        ("*", "Lock"): "鎖定",
        ("*", "Split Alpha"): "拆分 Alpha",
        ("*", "Mode"): "模式",
        ("*", "None"): "無",
        ("*", "Pixels"): "像素",
        ("*", "Percent"): "百分比",
        ("*", "W"): "寬",
        ("*", "H"): "高",
        ("*", "Scale"): "縮放",
        ("*", "Images per Cycle"): "每週期處理圖像數",
        ("*", "Number of images per timer cycle. Large values may freeze Blender."): "每個計時週期處理的圖像數量。數值過大可能導致 Blender 卡頓。",
        ("*", "Preserve Aspect Ratio"): "保持寬高比",
        ("*", "Use Compositor"): "使用合成器",
        ("*", "Apply selected compositor node tree before final save"): "在最終儲存前套用選中的合成器節點樹",
        ("*", "Node Tree"): "節點樹",
        ("*", "Select compositor node tree"): "選擇合成器節點樹",
        ("*", "-- Select Node Tree --"): "-- 選擇節點樹 --",
        ("*", "Choose a compositor node tree"): "選擇一個合成器節點樹",
        ("*", "-- No Node Trees --"): "-- 無節點樹 --",
        ("*", "Create a compositor tree first"): "請先建立一個合成器節點樹",
        ("*", "Nodes: {}"): "節點數：{}",
        
        # 操作類 (bl_label)
        ("*", "Convert"): "轉換",
        
        # 面板標題
        ("*", "Batch Texture Converter"): "批量紋理轉換器",
        ("*", "Path"): "路徑",
        ("*", "Format Configuration"): "格式配置",
        ("*", "Resize"): "調整大小",
        ("*", "Batch Processing"): "批量處理",
        ("*", "Large numbers may freeze Blender."): "數值過大可能導致 Blender 卡頓。",
        ("*", "Alpha"): "Alpha",
        ("*", "This format has poor alpha support."): "此格式對 Alpha 通道支援不佳。",
        ("*", "Splitting alpha is recommended."): "建議拆分 Alpha 通道。",
        ("*", "Compositor Processing"): "合成器處理",
        ("*", "Process via:"): "處理方式：",
        ("*", "Image node > your nodes > File Output node."): "圖像節點 > 您的節點 > 檔案輸出節點。",
        ("*", "Must be set up correctly, otherwise skipped."): "必須正確設定，否則將被跳過。",
        ("*", "Enable to use compositor node trees"): "啟用後可使用合成器節點樹",
        
        # 按鈕文本
        ("*", "Run Batch Conversion"): "執行批量轉換",
        
        # 報告資訊
        ("*", "Conversion Cancelled by User"): "使用者取消轉換",
        ("*", "Converting: {:.1f}% (Press ESC to Cancel)"): "正在轉換：{:.1f}%（按 ESC 取消）",
        ("*", "Video formats not supported"): "不支援影片格式",
        ("*", "Video formats NOT supported"): "不支援影片格式",
    },
}