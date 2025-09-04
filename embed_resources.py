import os
import shutil
import sys
import io
from pathlib import Path
from PyQt5.QtCore import QLibraryInfo  # 新增导入

# 设置 UTF-8 编码
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

def get_qt_plugins_path():
    """动态获取当前环境的 Qt 插件路径"""
    try:
        # 使用 PyQt5 的内置方法获取插件路径
        return QLibraryInfo.location(QLibraryInfo.PluginsPath)
    except AttributeError:
        # 兼容旧版 PyQt5
        return QLibraryInfo.path(QLibraryInfo.PluginsPath)

def embed_qt_resources():
    """嵌入 Qt 资源到包中"""
    # 动态获取 Qt 插件路径
    qt_plugins_dir = get_qt_plugins_path()
    dest_dir = "qt_plugins"

    print(f"源 Qt 插件目录: {qt_plugins_dir}")
    print(f"目标目录: {dest_dir}")

    # 确保源目录存在
    if not os.path.exists(qt_plugins_dir):
        print(f"错误: Qt 插件目录不存在: {qt_plugins_dir}")
        return

    # 清空目标目录
    if os.path.exists(dest_dir):
        print(f"删除现有目录: {dest_dir}")
        shutil.rmtree(dest_dir)

    # 创建目标目录结构
    os.makedirs(dest_dir, exist_ok=True)

    # 复制整个插件目录
    print("开始复制 Qt 插件...")
    shutil.copytree(qt_plugins_dir, os.path.join(dest_dir, "plugins"))

    print(f"Qt 资源已成功复制到: {os.path.join(dest_dir, 'plugins')}")

if __name__ == "__main__":
    embed_qt_resources()