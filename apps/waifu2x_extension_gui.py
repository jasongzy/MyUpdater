#!G:\Programs\anaconda3\envs\pytest\python.exe
import os
import re
import sys
from time import sleep

sys.path.append("..")

import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/AaronFeng753/Waifu2x-Extension-GUI

PROXY_DICT = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
LOCAL_DIR = r"E:\GreenSoft\Media\Waifu2x-Extension-GUI-Portable (图片放大)"
REPO = "AaronFeng753/Waifu2x-Extension-GUI"
# RELEASE_FILE_NAME = "Waifu2x-Extension-GUI-v0.0.0-Win64.7z"
TMP_DIR = os.environ.get("TEMP")

PATH_IDM = r"E:\GreenSoft\Network\Internet Download Manager\IDMan.exe"
PATH_7Z = r"E:\GreenSoft\Portable\PortableApps\PortableApps\\7-ZipPortable\App\\7-Zip64\\7z.exe"
waifu_config_path = os.path.join(LOCAL_DIR, r"waifu2x-extension-gui\settings.ini")

app = GitHubRelease(REPO)
app.local_dir = LOCAL_DIR
app.exe_path = os.path.join(
    LOCAL_DIR, r"waifu2x-extension-gui\Waifu2x-Extension-GUI-Launcher.exe"
)


def get_waifu_version():
    local_version = "0.0.0.0"
    try:
        waifu_config = file_io.get_config(waifu_config_path)
        local_version = waifu_config["settings"]["VERSION"]
    except:
        print("未找到 Waifu2x Extension GUI 当前版本！")
    return local_version


def init():
    app.local_version = get_waifu_version()
    app.check_release(False, PROXY_DICT)
    # Release 文件名包含版本号
    app.release_file_name = "Waifu2x-Extension-GUI-" + app.latest_version + "-Win64.7z"
    # app.release_file_url = app.get_download_url()
    # 采用提供的超星云盘直链
    if app.release_body:
        app.release_file_url = re.findall(
            r"http://d0.ananas.chaoxing.com[^\s]*7z", app.release_body
        )[0]


def update(silent=False):
    tmp_file = os.path.join(TMP_DIR, app.release_file_name)
    if file_io.downloader_idm(PATH_IDM, app.release_file_url, tmp_file):
        return -1
    file_io.empty_dir_interact(LOCAL_DIR, True, [], not silent)
    file_io.unpack_7z(PATH_7Z, tmp_file, LOCAL_DIR)
    # 打开程序以更新settings.ini
    os.popen(
        os.path.join(LOCAL_DIR, r"waifu2x-extension-gui\Waifu2x-Extension-GUI.exe")
    )
    sleep(5)
    file_io.terminate_process("Waifu2x-Extension-GUI.exe")
    app.local_version = get_waifu_version()
    if app.is_latest() == 1:
        os.remove(tmp_file)
        print("Waifu2x Extension GUI %s 更新成功！" % app.local_version)
        return 0
    else:
        print("校验失败，请重新下载！")
        return -1


if __name__ == "__main__":
    init()
    app.update_interact(update)
