#!G:\Programs\anaconda3\envs\pytest\python.exe
import os
import sys

sys.path.append("..")
import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/kmvan/x-prober

PROXY_DICT = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
LOCAL_DIR = r"E:\Tech\Linux\Server"
REPO = "kmvan/x-prober"
RELEASE_FILE_NAME = "prober.php"
# TMP_DIR = os.environ.get("TEMP")

current_filename = ""


app = GitHubRelease(REPO, RELEASE_FILE_NAME)
app.local_dir = LOCAL_DIR


def get_prober_version():
    local_version = "0.0.0.0"
    global current_filename
    for item in os.listdir(LOCAL_DIR):
        if item.startswith("xprober"):
            current_filename = item
    if not current_filename:
        print("未找到 X Prober 当前版本！")
    else:
        try:
            local_version = os.path.splitext(current_filename)[0].split("_")[1]
        except:
            print("未找到 X Prober 当前版本！")
    return local_version


def init():
    app.local_version = get_prober_version()
    app.check_release(False, PROXY_DICT)


def update(silent=False):
    old_file = os.path.join(LOCAL_DIR, current_filename)
    new_file = os.path.join(LOCAL_DIR, "xprober_" + app.latest_version + ".php")
    if file_io.downloader(app.release_file_url, new_file, PROXY_DICT, silent):
        return -1
    app.local_version = get_prober_version()
    if app.is_latest() == 1:
        os.remove(old_file)
        print("X Prober %s 更新成功！" % app.local_version)
        return 0
    else:
        print("校验失败，请重新下载！")
        return -1


if __name__ == "__main__":
    init()
    app.update_interact(update)
