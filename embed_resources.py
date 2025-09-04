import os
import shutil
import sys
from pathlib import Path


def embed_qt_resources():
    """跨平台嵌入 Qt 资源"""
    # 确定 PyQt5 安装路径
    try:
        import PyQt5
        pyqt_path = Path(PyQt5.__file__).parent
        qt_plugins_dir = pyqt_path / "Qt5" / "plugins"
    except ImportError:
        # 备选路径
        if sys.platform == "win32":
            default_path = Path(os.environ.get("PROGRAMFILES",
                                               "C:\\")) / "Python" / "Lib" / "site-packages" / "PyQt5" / "Qt5" / "plugins"
        elif sys.platform == "darwin":
            default_path = Path("/usr/local/lib/python3.8/site-packages/PyQt5/Qt5/plugins")
        else:  # Linux
            default_path = Path("/usr/lib/python3/dist-packages/PyQt5/Qt5/plugins")

        qt_plugins_dir = default_path if default_path.exists() else Path.cwd() / "qt_plugins"

    dest_dir = Path("qt_plugins")

    print(f"源 Qt 插件目录: {qt_plugins_dir}")
    print(f"目标目录: {dest_dir}")

    # 清空目标目录
    if dest_dir.exists():
        print(f"删除现有目录: {dest_dir}")
        shutil.rmtree(dest_dir)

    # 创建目标目录
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 复制整个插件目录
    print("开始复制 Qt 插件...")
    shutil.copytree(qt_plugins_dir, dest_dir / "plugins")

    print(f"Qt 资源已成功复制到: {dest_dir / 'plugins'}")

    # macOS 特殊处理
    if sys.platform == "darwin":
        print("执行 macOS 额外处理...")
        os.system(
            "find qt_plugins -name '*.dylib' -exec install_name_tool -add_rpath @executable_path/../qt_plugins/plugins {} \;")


if __name__ == "__main__":
    embed_qt_resources()