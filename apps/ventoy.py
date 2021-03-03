#!G:\Programs\anaconda3\envs\pytest\python.exe
import os
import sys

sys.path.append("..")
import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/ventoy/Ventoy

PROXY_DICT = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
LOCAL_DIR = r"E:\GreenSoft\Utilities\ventoy (多系统U盘启动盘制作)"
REPO = "ventoy/Ventoy"
# RELEASE_FILE_NAME = "ventoy-0.0.0.0-windows.zip"
TMP_DIR = os.environ.get("TEMP")

WHITE_LIST = [
    "manual_for_ventoy_with_secure_boot.png",
    "secure_cn.png",
    "Ventoy2Disk.ini",
]
release_name = ""

app = GitHubRelease(REPO)
app.local_dir = LOCAL_DIR
app.exe_path = os.path.join(LOCAL_DIR, "Ventoy2Disk.exe")


def get_ventoy_version():
    path = os.path.join(LOCAL_DIR, "ventoy/version")
    local_version = "0.0.0.0"
    try:
        with open(path, "r") as f:
            local_version = f.readline().replace("\n", "")
    except:
        print("未找到 Ventoy 当前版本！")
    return local_version


def init():
    app.local_version = get_ventoy_version()
    app.check_release(False, PROXY_DICT)
    # Release 文件名包含版本号
    global release_name
    release_name = "ventoy-" + str(app.latest_version[1:])
    app.release_file_name = release_name + "-windows.zip"
    app.release_file_url = app.get_download_url()


def update(silent=False):
    tmp_file = os.path.join(TMP_DIR, app.release_file_name)
    if file_io.downloader(app.release_file_url, tmp_file, PROXY_DICT, silent):
        return -1
    file_io.empty_dir_interact(LOCAL_DIR, True, WHITE_LIST, not silent)
    file_io.unpack_zip(tmp_file, LOCAL_DIR)
    file_io.cut_dir(os.path.join(LOCAL_DIR, release_name), LOCAL_DIR)
    app.local_version = get_ventoy_version()
    if app.is_latest() == 1:
        os.remove(tmp_file)
        print("Ventoy %s 更新成功！" % app.local_version)
        return 0
    else:
        print("校验失败，请重新下载！")
        return -1


if __name__ == "__main__":
    init()
    app.update_interact(update)
