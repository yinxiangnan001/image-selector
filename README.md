# Image Selector

基于 Streamlit 的图像浏览与筛选工具。从指定文件夹加载图像，以分页网格形式展示，通过勾选 checkbox 挑选图像，选中的图像会被复制到 `selected` 文件夹中。

## 依赖安装

```bash
pip install streamlit pillow numpy
```

## 启动

```bash
streamlit run image_selector.py
```

## 使用方法

1. 在左侧边栏输入图像文件夹的绝对路径
2. 可调整每行列数（默认 5 列）和每页展示张数（默认 15 张）
3. 勾选想要保留的图像，点击「✅ 提交选择」按钮确认
4. 选中的图像会被复制到图像文件夹同级目录下的 `selected/` 文件夹中
5. 取消勾选并提交会从 `selected/` 中移除对应图像
6. 使用底部翻页按钮浏览更多图像

## 支持的图像格式

PNG、JPG、JPEG、BMP、TIFF、WebP

## 说明

- 带透明通道（RGBA）的图像会以绿色背景渲染预览，方便查看透明区域

