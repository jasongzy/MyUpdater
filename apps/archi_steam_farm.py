#!G:\Programs\anaconda3\envs\pytest\python.exe
import os
import sys

# from lxml import etree

sys.path.append("..")
import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/JustArchiNET/ArchiSteamFarm

PROXY_DICT = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
LOCAL_DIR = r"E:\GreenSoft\Entertainment\ArchiSteamFarm (Steam云挂卡)"
REPO = "JustArchiNET/ArchiSteamFarm"
RELEASE_FILE_NAME = "ASF-win-x64.zip"
TMP_DIR = os.environ.get("TEMP")

app = GitHubRelease(REPO, RELEASE_FILE_NAME)
app.local_dir = LOCAL_DIR
app.exe_path = os.path.join(LOCAL_DIR, "ArchiSteamFarm.exe")


# def get_asf_version():
#     path = os.path.join(LOCAL_DIR, "Changelog.html")
#     local_version = "0.0.0.0"
#     try:
#         with open(path, "r") as f:
#             changelog = f.read()
#         local_version = str(etree.HTML(changelog).xpath("/html/head/meta/@content")[0])
#         local_version = local_version.split("/")[-1]
#     except:
#         print("未找到 ArchiSteamFarm 当前版本！")
#     return local_version


def init():
    # app.local_version = get_asf_version()
    app.local_version = file_io.get_exe_version(app.exe_path)
    app.check_release(False, PROXY_DICT)


def update(silent=False):
    tmp_file = os.path.join(TMP_DIR, app.release_file_name)
    if file_io.downloader(app.release_file_url, tmp_file, PROXY_DICT, silent):
        return -1
    file_io.empty_dir_interact(LOCAL_DIR, True, [], not silent)
    file_io.unpack_zip(tmp_file, LOCAL_DIR)
    # app.local_version = get_asf_version()
    app.local_version = file_io.get_exe_version(app.exe_path)
    if app.is_latest() == 1:
        os.remove(tmp_file)
        print("ArchiSteamFarm %s 更新成功！" % app.local_version)
        return 0
    else:
        print("校验失败，请重新下载！")
        return -1


if __name__ == "__main__":
    init()
    app.update_interact(update)
