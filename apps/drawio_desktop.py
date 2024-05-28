import os
import sys

sys.path.append("..")
import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/jgraph/drawio-desktop

ID = "drawio"
REPO = "jgraph/drawio-desktop"
FILENAME = "draw.io-windows-no-installer.exe"

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
        app.release_file_url = app.get_download_url(version_replace=True)


def update(verbose=True):
    file = os.path.join(app.local_dir, FILENAME)
    if os.path.isfile(file):
        file_io.send2trash(file)
    if file_io.downloader(app.release_file_url, file, file_io.get_config("common", "proxy_dict"), verbose=verbose):
        return -1
    app.local_version = file_io.get_exe_version(app.exe_path)
    if app.is_latest() == 1:
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
