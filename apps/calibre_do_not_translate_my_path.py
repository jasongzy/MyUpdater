import os
import sys

sys.path.append("..")
import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/Cirn09/calibre-do-not-translate-my-path

ID = "calibre_dntmp"
REPO = "Cirn09/calibre-do-not-translate-my-path"
TMP_DIR = os.environ.get("TEMP")
FILENAME = "calibre.exe"
LIB_PATH = os.path.join("app", "bin", "python-lib.bypy.frozen")

app = GitHubRelease(REPO)


def get_calibre_lib_version():
    path = os.path.join(app.local_dir, "python-lib-version")
    local_version = "0.0.0.0"
    try:
        with open(path, "r") as f:
            version = f.readline().replace("\n", "")
            if version:
                local_version = version
    except Exception as e:
        print(f"{path} 读取失败: {e}")
    return local_version


def write_calibre_lib_version(version: str):
    path = os.path.join(app.local_dir, "python-lib-version")
    try:
        with open(path, "w") as f:
            f.write(version)
    except Exception as e:
        print(f"{path} 写入失败：{e}")


def init(check_release=True):
    app.local_dir = file_io.get_config(ID, "path")
    if not os.path.isdir(app.local_dir):
        print(f'本地目录配置有误："{app.local_dir}" 不存在！')
        return
    app.exe_path = os.path.join(app.local_dir, FILENAME)
    # app.local_version = file_io.get_exe_version(app.exe_path)
    app.local_version = get_calibre_lib_version()
    include_pre = file_io.get_config(ID, "pre_release")
    if include_pre:
        try:
            include_pre = int(include_pre)
        except TypeError:
            print(f"[{ID}] Pre-release 开关配置有误")
            include_pre = 0
    if check_release:
        app.check_release(
            include_pre,
            file_io.get_config("common", "proxy_dict"),
            file_io.get_config("common", "github_oauth"),
        )
        app.release_file_name = file_io.get_config(ID, "release_file")
        app.release_file_url = app.get_download_url(fuzzy=True)


def update(verbose=True):
    tmp_file = os.path.join(TMP_DIR, app.release_file_name)
    if file_io.downloader(app.release_file_url, tmp_file, file_io.get_config("common", "proxy_dict"), verbose=verbose):
        return -1
    lib_path = os.path.join(app.local_dir, LIB_PATH)
    if os.path.isfile(lib_path):
        lib_path_bak = f"{lib_path}.bak"
        if os.path.isfile(lib_path_bak):
            os.remove(lib_path_bak)
        os.rename(lib_path, lib_path_bak)
        print(f"备份 {lib_path} 成功！")
    else:
        print("未找到文件：", lib_path)
    file_io.unpack(tmp_file, app.local_dir)
    lib_path_unzip = os.path.join(app.local_dir, "Calibre2", LIB_PATH)
    os.rename(lib_path_unzip, lib_path)
    os.removedirs(os.path.dirname(lib_path_unzip))
    # app.local_version = file_io.get_exe_version(app.exe_path)
    if not os.path.isfile(lib_path):
        print("未找到 python-lib 文件，请重新下载！")
        return -1
    write_calibre_lib_version(app.latest_version)
    app.local_version = get_calibre_lib_version()
    if app.is_latest() == 1:
        os.remove(tmp_file)
        print(f"{file_io.get_config(ID, 'name', ID)} {app.local_version} 更新成功！")
        return 0
    else:
        print("校验失败，请重新下载！")
        return -1


if __name__ == "__main__":
    if file_io.update_config("../config.ini"):
        sys.exit(1)
    init()
    app.update_interact(update)
