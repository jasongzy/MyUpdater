import os
import re
import sys
from time import sleep

sys.path.append("..")

import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/AaronFeng753/Waifu2x-Extension-GUI

ID = "waifu"
REPO = "AaronFeng753/Waifu2x-Extension-GUI"
TMP_DIR = os.environ.get("TEMP")
FILENAME = "Waifu2x-Extension-GUI-Start.bat"

app = GitHubRelease(REPO)


def get_waifu_version():
    local_version = "0.0.0.0"
    try:
        waifu_config = file_io.read_config(os.path.join(app.local_dir, r"waifu2x-extension-gui\settings.ini"))
        local_version = waifu_config["settings"]["VERSION"]
    except:
        print("未找到 Waifu2x Extension GUI 当前版本！")
    return local_version


def init(check_release=True):
    app.local_dir = file_io.get_config(ID, "path")
    if not os.path.isdir(app.local_dir):
        print('本地目录配置有误："' + app.local_dir + '" 不存在！')
        return
    app.exe_path = os.path.join(app.local_dir, FILENAME)
    app.local_version = get_waifu_version()
    include_pre = file_io.get_config(ID, "pre_release")
    if include_pre:
        try:
            include_pre = int(include_pre)
        except:
            print("[%s] Pre-release 开关配置有误" % ID)
            include_pre = 0
    if check_release:
        app.check_release(
            include_pre, file_io.get_config("common", "proxy_dict"), file_io.get_config("common", "github_oauth"),
        )
        # Release 文件名包含版本号
        # 在配置文件中用$代替
        #! 支持增量更新：模糊查找
        app.release_file_name = file_io.get_config(ID, "release_file").split("$", 1)[0]
        app.release_file_url = app.get_download_url(True)


def update(silent=False):
    tmp_file = os.path.join(TMP_DIR, app.release_file_name)
    # if file_io.downloader_idm(
    #     file_io.get_config("common", "idm_path"), app.release_file_url, tmp_file
    # ):
    if file_io.downloader(app.release_file_url, tmp_file, file_io.get_config("common", "proxy_dict"), silent,):
        return -1
    # file_io.empty_dir_interact(app.local_dir, True, [], not silent)
    file_io.unpack_7z(file_io.get_config("common", "7z_path"), tmp_file, app.local_dir)
    # 打开程序以更新settings.ini
    pwd = os.getcwd()
    os.chdir(os.path.join(app.local_dir))
    os.popen(app.exe_path)
    os.chdir(pwd)
    sleep(15)
    # file_io.terminate_process("Waifu2x-Extension-GUI.exe")
    app.local_version = get_waifu_version()
    if app.is_latest() == 1:
        os.remove(tmp_file)
        print("Waifu2x Extension GUI %s 更新成功！" % app.local_version)
        return 0
    else:
        print("校验失败，请重新下载！")
        return -1


if __name__ == "__main__":
    if file_io.update_config("../config.ini"):
        exit(1)
    init()
    app.update_interact(update)
