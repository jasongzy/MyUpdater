import os
import sys

sys.path.append("..")
import utils.file_io as file_io
from utils.github_release import GitHubRelease

# https://github.com/Genymobile/scrcpy

ID = "scrcpy"
REPO = "Genymobile/scrcpy"
TMP_DIR = os.environ.get("TEMP")
FILENAME = "scrcpy.exe"

app = GitHubRelease(REPO)


def get_scrcpy_version():
    path = os.path.join(app.local_dir, FILENAME)
    out = os.popen(f'"{path}" -v 2>&1').readline().strip()
    local_version = "0.0.0.0"
    try:
        assert out.startswith("scrcpy")
        version = out.split(" ")[1]
        if version:
            local_version = version
    except (AssertionError, IndexError):
        print("未找到 scrcpy 本地版本！")
    return local_version


def init(check_release=True):
    app.local_dir = file_io.get_config(ID, "path")
    if not os.path.isdir(app.local_dir):
        print(f'本地目录配置有误："{app.local_dir}" 不存在！')
        return
    app.exe_path = os.path.join(app.local_dir, FILENAME)
    app.local_version = get_scrcpy_version()
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
    tmp_file = os.path.join(TMP_DIR, app.release_file_name)
    if file_io.downloader(app.release_file_url, tmp_file, file_io.get_config("common", "proxy_dict"), verbose=verbose):
        return -1
    whitelist = file_io.get_config(ID, "whitelist").split(",")
    whitelist = list(map(str.strip, whitelist))
    whitelist = list(filter(None, whitelist))
    if file_io.empty_dir_interact(app.local_dir, True, whitelist, verbose=verbose) != 0:
        return -1
    file_io.unpack(tmp_file, app.local_dir)
    file_io.cut_dir(
        os.path.join(app.local_dir, f"{os.path.basename(app.local_dir)}-{app.latest_version}"),
        app.local_dir,
    )
    app.local_version = get_scrcpy_version()
    if app.is_latest() == 1:
        os.remove(tmp_file)
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
