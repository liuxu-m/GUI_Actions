import os
import shutil
import py_compile
from pathlib import Path


def embed_qt_resources():
    """嵌入 Qt 资源到包中"""
    # 设置源路径和目标路径
    qt_plugins_dir = r"C:\Users\liuxu001\AppData\Local\Programs\Python\Python38\Lib\site-packages\PyQt5\Qt5\plugins"
    dest_dir = "qt_plugins"

    print(f"源 Qt 插件目录: {qt_plugins_dir}")
    print(f"目标目录: {dest_dir}")

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