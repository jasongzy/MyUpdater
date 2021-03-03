#!G:\Programs\anaconda3\envs\pytest\python.exe
import os
import sys

sys.path.append("..")
import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/Fndroid/clash_for_windows_pkg

PROXY_DICT = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
LOCAL_DIR = r"E:\GreenSoft\Network\Clash.for.Windows"
REPO = "Fndroid/clash_for_windows_pkg"
# RELEASE_FILE_NAME = "Clash.for.Windows-0.0.0-win.7z"
TMP_DIR = os.environ.get("TEMP")

PATH_7Z = r"E:\GreenSoft\Portable\PortableApps\PortableApps\\7-ZipPortable\App\\7-Zip64\\7z.exe"

app = GitHubRelease(REPO)
app.local_dir = LOCAL_DIR
app.exe_path = os.path.join(LOCAL_DIR, "Clash for Windows.exe")


def init():
    app.local_version = file_io.get_exe_version(app.exe_path)
    app.check_release(False, PROXY_DICT)
    # Release 文件名包含版本号
    app.release_file_name = "Clash.for.Windows-" + app.latest_version + "-win.7z"
    app.release_file_url = app.get_download_url()


def update(silent=False):
    tmp_file = os.path.join(TMP_DIR, app.release_file_name)
    if file_io.downloader(app.release_file_url, tmp_file, PROXY_DICT, silent):
        return -1
    file_io.terminate_process("Clash for Windows.exe", not silent)
    file_io.empty_dir_interact(LOCAL_DIR, True, [], not silent)
    file_io.unpack_7z(PATH_7Z, tmp_file, LOCAL_DIR)
    app.local_version = file_io.get_exe_version(app.exe_path)
    if app.is_latest() == 1:
        os.remove(tmp_file)
        print("Clash for Windows %s 更新成功！" % app.local_version)
        os.popen('"%s"' % app.exe_path)
        return 0
    else:
        print("校验失败，请重新下载！")
        return -1


if __name__ == "__main__":
    init()
    app.update_interact(update)
