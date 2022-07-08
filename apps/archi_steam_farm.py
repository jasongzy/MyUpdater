import os
import sys

# from lxml import etree

sys.path.append("..")
import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/JustArchiNET/ArchiSteamFarm

ID = "asf"
REPO = "JustArchiNET/ArchiSteamFarm"
TMP_DIR = os.environ.get("TEMP")
FILENAME = "ArchiSteamFarm.exe"

app = GitHubRelease(REPO)


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


def init(check_release=True):
    app.release_file_name = file_io.get_config(ID, "release_file")
    app.local_dir = file_io.get_config(ID, "path")
    if not os.path.isdir(app.local_dir):
        print('本地目录配置有误："' + app.local_dir + '" 不存在！')
        return
    app.exe_path = os.path.join(app.local_dir, FILENAME)
    # app.local_version = get_asf_version()
    app.local_version = file_io.get_exe_version(app.exe_path)
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


def update(verbose=True):
    tmp_file = os.path.join(TMP_DIR, app.release_file_name)
    if file_io.downloader(app.release_file_url, tmp_file, file_io.get_config("common", "proxy_dict"), verbose=verbose):
        return -1
    whitelist = file_io.get_config(ID, "whitelist").split(",")
    whitelist = list(map(str.strip, whitelist))
    whitelist = list(filter(None, whitelist))
    if file_io.empty_dir_interact(app.local_dir, True, whitelist, verbose=verbose) != 0:
        return -1
    file_io.unpack_zip(tmp_file, app.local_dir)
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
    if file_io.update_config("../config.ini"):
        sys.exit(1)
    init()
    app.update_interact(update)
