import os
import sys
from tempfile import NamedTemporaryFile

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
import utils.file_io as file_io
from utils.github_release import GitHubRelease

ID = "argus"
REPO = "Ray-lea/Argus"
FILENAME = "Argus_x64.exe"

app = GitHubRelease(REPO)


def init(check_release: bool = True) -> None:
    app.local_dir = file_io.get_config(ID, "path")
    app.exe_path = os.path.join(app.local_dir, FILENAME)
    if not os.path.isdir(app.local_dir):
        print(f'本地目录配置有误："{app.local_dir}" 不存在！')
        return
    app.local_version = file_io.get_exe_version(app.exe_path)
    if check_release:
        try:
            include_pre = int(file_io.get_config(ID, "pre_release") or 0)
        except ValueError:
            print(f"[{ID}] Pre-release 开关配置有误")
            include_pre = 0
        app.check_release(
            include_pre,
            file_io.get_config("common", "proxy_dict"),
            file_io.get_config("common", "github_oauth"),
        )
        app.release_file_name = file_io.get_config(ID, "release_file")
        app.release_file_url = app.get_download_url(version_replace=True)


def update(verbose: bool = True) -> int:
    try:
        with NamedTemporaryFile(dir=app.local_dir, prefix="Argus_", suffix=".tmp", delete=False) as tmp:
            tmp_file = tmp.name
        try:
            proxy = file_io.get_config("common", "proxy_dict")
            if file_io.downloader(app.release_file_url, tmp_file, proxy, verbose=verbose, overwrite=True):
                return -1
            info = file_io.getFileProperties(tmp_file)
            if (info["StringFileInfo"] or {}).get("ProductVersion") != app.latest_version.removeprefix("v"):
                print("校验失败，请重新下载！")
                return -1
            if os.path.isfile(app.exe_path) and file_io.send2trash(os.path.abspath(app.exe_path)):
                print(f"旧版 {FILENAME} 移入回收站失败。")
                return -1
            os.rename(tmp_file, app.exe_path)
            app.local_version = info["FileVersion"]
        finally:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
    except OSError as e:
        print(f"Argus 更新失败：{e}")
        return -1
    print(f"{file_io.get_config(ID, 'name', ID)} {app.local_version} 更新成功！")
    return 0


if __name__ == "__main__":
    if file_io.update_config(os.path.join(ROOT_DIR, "config.ini")):
        sys.exit(1)
    init()
    app.update_interact(update)
