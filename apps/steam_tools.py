import os
import sys
from time import sleep

sys.path.append("..")
import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/BeyondDimension/SteamTools

ID = "steamtools"
REPO = "BeyondDimension/SteamTools"
TMP_DIR = os.environ.get("TEMP")
FILENAME = "Steam++.exe"

app = GitHubRelease(REPO)


def init(check_release=True):
    app.local_dir = file_io.get_config(ID, "path")
    if not os.path.isdir(app.local_dir):
        print(f'本地目录配置有误："{app.local_dir}" 不存在！')
        return
    app.exe_path = os.path.join(app.local_dir, FILENAME)
    app.local_version = file_io.get_exe_version(app.exe_path)
    include_pre = file_io.get_config(ID, "pre_release")
    if include_pre:
        try:
            include_pre = int(include_pre)
        except:
            print(f"[{ID}] Pre-release 开关配置有误")
            include_pre = 0
    if check_release:
        app.check_release(
            include_pre,
            file_io.get_config("common", "proxy_dict"),
            file_io.get_config("common", "github_oauth"),
        )
        # Release 文件名包含版本号
        # 在配置文件中用$代替
        # !但实际版本号与文件名并不总是一致，因此采用模糊查找
        app.release_file_name = file_io.get_config(ID, "release_file").split("$", 1)[0]
        app.release_file_url = app.get_download_url(fuzzy=True, ext="7z")


def update(verbose=True):
    tmp_file = os.path.join(TMP_DIR, app.release_file_name)
    if file_io.downloader(app.release_file_url, tmp_file, file_io.get_config("common", "proxy_dict"), verbose=verbose):
        return -1
    whitelist = file_io.get_config(ID, "whitelist").split(",")
    whitelist = list(map(str.strip, whitelist))
    whitelist = list(filter(None, whitelist))
    if file_io.empty_dir_interact(app.local_dir, True, whitelist, verbose=verbose) != 0:
        return -1
    file_io.unpack_7z(file_io.get_config("common", "7z_path"), tmp_file, app.local_dir)
    app.local_version = file_io.get_exe_version(app.exe_path)
    if app.is_latest() == 1:
        os.remove(tmp_file)
        print("{} {} 更新成功！".format(file_io.get_config(ID, "name", ID), app.local_version))
        return 0
    else:
        print("校验失败，请重新下载！")
        return -1


if __name__ == "__main__":
    if file_io.update_config("../config.ini"):
        sys.exit(1)
    init()
    app.update_interact(update)
