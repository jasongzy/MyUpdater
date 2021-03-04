#!G:\Programs\anaconda3\envs\pytest\python.exe
import os
import sys

sys.path.append("..")
import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/kmvan/x-prober

ID = "xprober"
REPO = "kmvan/x-prober"

app = GitHubRelease(REPO)


def get_prober_version():
    local_version = "0.0.0.0"
    global current_filename
    for item in os.listdir(app.local_dir):
        if item.startswith("xprober_") and (not item.endswith(".old")):
            current_filename = item
    if not current_filename:
        print("未找到 X Prober 当前版本！")
    else:
        version = os.path.splitext(current_filename)[0].split("_")[1]
        if version:
            local_version = version
        else:
            print("未找到 X Prober 当前版本！")
    return local_version


def init(check_release=True):
    app.release_file_name = file_io.get_config(ID, "release_file")
    app.local_dir = file_io.get_config(ID, "path")
    if not os.path.isdir(app.local_dir):
        print('本地目录配置有误："' + app.local_dir + '" 不存在！')
        return
    app.local_version = get_prober_version()
    app.exe_path = os.path.join(app.local_dir, current_filename)
    include_pre = file_io.get_config(ID, "pre_release")
    if include_pre:
        try:
            include_pre = int(include_pre)
        except:
            print("[%s] Pre-release 开关配置有误" % ID)
            include_pre = 0
    if check_release:
        app.check_release(
            include_pre,
            file_io.get_config("common", "proxy_dict"),
            file_io.get_config("common", "github_oauth"),
        )


def update(silent=False):
    old_file = os.path.join(app.local_dir, current_filename)
    new_file = os.path.join(app.local_dir, "xprober_" + app.latest_version + ".php")
    if file_io.downloader(
        app.release_file_url,
        new_file,
        file_io.get_config("common", "proxy_dict"),
        silent,
    ):
        return -1
    os.rename(old_file, old_file + ".old")
    old_file += ".old"
    app.local_version = get_prober_version()
    if app.is_latest() == 1:
        os.remove(old_file)
        print("X Prober %s 更新成功！" % app.local_version)
        return 0
    else:
        print("校验失败，请重新下载！")
        return -1


if __name__ == "__main__":
    if file_io.update_config("../config.ini"):
        exit(1)
    init()
    app.update_interact(update)
