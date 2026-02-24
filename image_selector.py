import streamlit as st
from PIL import Image
import numpy as np
import os
import shutil
import glob
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Image Selector", layout="wide")

folder = st.sidebar.text_input("图像文件夹路径", value="")
COLS = st.sidebar.selectbox("每行列数", [1, 2, 3, 4, 5, 6], index=4)
PER_PAGE = st.sidebar.selectbox("每页展示张数", list(range(5, 51, 5)), index=2)

if not folder or not os.path.isdir(folder):
    st.info("请在左侧输入有效的图像文件夹路径。")
    st.stop()

selected_dir = os.path.join(os.path.dirname(os.path.abspath(folder)), "selected")
os.makedirs(selected_dir, exist_ok=True)

# 收集所有图像
exts = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff", "*.webp")
files = []
for ext in exts:
    files.extend(glob.glob(os.path.join(folder, ext)))
files = sorted(files)

if not files:
    st.warning("该文件夹下没有找到图像文件。")
    st.stop()

selected_names = set(os.listdir(selected_dir)) if os.path.isdir(selected_dir) else set()

# 根据 selected 中最后一张图定位起始页
if "page_initialized" not in st.session_state:
    st.session_state.page_initialized = True
    if selected_names:
        last_file = max(
            (os.path.join(selected_dir, n) for n in selected_names),
            key=os.path.getmtime
        )
        last_name = os.path.basename(last_file)
        filenames = [os.path.basename(f) for f in files]
        if last_name in filenames:
            next_idx = filenames.index(last_name) + 1
            st.session_state.page = min(next_idx // PER_PAGE, (len(files) - 1) // PER_PAGE)
        else:
            st.session_state.page = 0
    else:
        st.session_state.page = 0

if "page" not in st.session_state:
    st.session_state.page = 0

total = len(files)
total_pages = (total + PER_PAGE - 1) // PER_PAGE

st.caption(f"共 {total} 张图像，第 {st.session_state.page + 1}/{total_pages} 页 | 已选 {len(selected_names)} 张")

start = st.session_state.page * PER_PAGE
batch = files[start:start + PER_PAGE]


def render_with_green_bg(img):
    arr = np.array(img.convert("RGBA")).astype(np.float32)
    alpha = arr[:, :, 3:4] / 255.0
    green_bg = np.array([0, 255, 0], dtype=np.float32)
    rgb = arr[:, :, :3] * alpha + green_bg * (1 - alpha)
    return Image.fromarray(rgb.astype(np.uint8), "RGB")


def load_and_render(fpath):
    img = Image.open(fpath)
    img.load()
    display = render_with_green_bg(img) if img.mode == "RGBA" else img
    return fpath, display


# 并行加载
with ThreadPoolExecutor(max_workers=min(len(batch), 8)) as pool:
    results = dict(pool.map(load_and_render, batch))

# 瀑布流 + checkbox
col_bins = [[] for _ in range(COLS)]
for idx, fpath in enumerate(batch):
    col_bins[idx % COLS].append((start + idx, fpath))

cols = st.columns(COLS)
for col_idx, col in enumerate(cols):
    with col:
        for global_idx, fpath in col_bins[col_idx]:
            st.image(results[fpath], use_container_width=True)
            fname = os.path.basename(fpath)
            already_selected = fname in selected_names
            st.checkbox(
                fname,
                value=already_selected,
                key=f"chk_{global_idx}"
            )

# 提交按钮
if st.button("✅ 提交选择"):
    count = 0
    for idx, fpath in enumerate(batch):
        fname = os.path.basename(fpath)
        checked = st.session_state.get(f"chk_{start + idx}", False)
        dst = os.path.join(selected_dir, fname)
        if checked and not os.path.exists(dst):
            shutil.copy2(fpath, dst)
            count += 1
        elif not checked and os.path.exists(dst):
            os.remove(dst)
    st.success(f"已更新，本页新增 {count} 张")
    st.rerun()

# 翻页按钮
c_left, _, c_right = st.columns([1, 3, 1])
with c_left:
    if st.button("⬅ 上一页", disabled=st.session_state.page <= 0):
        st.session_state.page -= 1
        st.rerun()
with c_right:
    if st.button("下一页 ➡", disabled=st.session_state.page >= total_pages - 1):
        st.session_state.page += 1
        st.rerun()
