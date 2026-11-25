import os
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

import win32api
import win32security

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
import utils.file_io as file_io
from utils.github_release import GitHubRelease

ID = "localsend"
FILENAME = "localsend_app.exe"
app = GitHubRelease("localsend/localsend")


def get_localsend_version(exe_path: str) -> str:
    info = file_io.getFileProperties(exe_path)["StringFileInfo"] or {}
    if info.get("ProductName") != "LocalSend":
        return ""
    return (info.get("ProductVersion") or "").partition("+")[0]


def get_owner_sid(path: str) -> str:
    sd = win32security.GetNamedSecurityInfo(
        path, win32security.SE_FILE_OBJECT, win32security.OWNER_SECURITY_INFORMATION
    )
    return win32security.ConvertSidToStringSid(sd.GetSecurityDescriptorOwner())


def copy_install_acl(source: str, dest: str) -> None:
    flags = win32security.DACL_SECURITY_INFORMATION
    kind = win32security.SE_FILE_OBJECT
    sd = win32security.GetNamedSecurityInfo(source, kind, flags)
    if sd.GetSecurityDescriptorControl()[0] & win32security.SE_DACL_PROTECTED:
        flags |= win32security.PROTECTED_DACL_SECURITY_INFORMATION
    else:
        flags |= win32security.UNPROTECTED_DACL_SECURITY_INFORMATION
    win32security.SetNamedSecurityInfo(dest, kind, flags, None, None, sd.GetSecurityDescriptorDacl(), None)


def init(check_release: bool = True) -> None:
    app.local_dir = file_io.get_config(ID, "path")
    app.exe_path = os.path.join(app.local_dir, FILENAME)
    app.local_version = get_localsend_version(app.exe_path) or "0.0.0.0"
    if not os.path.isdir(app.local_dir):
        print(f'本地目录配置有误："{app.local_dir}" 不存在！')
        return
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
    if not os.path.isdir(app.local_dir):
        print(f'本地目录配置有误："{app.local_dir}" 不存在！')
        return -1
    if not app.release_file_url:
        print(f"未找到指定的 Release 文件！（{app.release_file_name}）")
        return -1
    local_dir = os.path.abspath(app.local_dir)
    backup = local_dir + ".old"
    try:
        with TemporaryDirectory() as tmp, TemporaryDirectory(dir=os.path.dirname(local_dir)) as staged:
            archive = os.path.join(tmp, "release.zip")
            proxy = file_io.get_config("common", "proxy_dict")
            if file_io.downloader(app.release_file_url, archive, proxy, verbose=verbose):
                return -1
            copy_install_acl(local_dir, staged)
            if file_io.unpack_zip(archive, staged):
                return -1
            version = get_localsend_version(os.path.join(staged, FILENAME))
            if not version or version != app.latest_version.removeprefix("v"):
                print("校验失败，请重新下载！")
                return -1
            settings = os.path.join(local_dir, "settings.json")
            if os.path.isfile(settings):
                new_settings = os.path.join(staged, "settings.json")
                with open(new_settings, "ab"):
                    pass
                copy_install_acl(settings, new_settings)
                shutil.copy2(settings, new_settings)
            owner = get_owner_sid(local_dir)
            if owner != get_owner_sid(staged):
                icacls = os.path.join(win32api.GetSystemDirectory(), "icacls.exe")
                subprocess.run(
                    [icacls, staged, "/setowner", f"*{owner}", "/T", "/L", "/Q"],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            os.rename(local_dir, backup)
            try:
                os.rename(staged, local_dir)
            except OSError:
                os.rename(backup, local_dir)
                raise
            app.local_version = version
            if file_io.send2trash(backup):
                print(f"旧目录移入回收站失败：{backup}")
    except (OSError, win32security.error, subprocess.CalledProcessError) as e:
        print(f"{file_io.get_config(ID, 'name', ID)} 更新失败：{e}")
        return -1
    print(f"{file_io.get_config(ID, 'name', ID)} {app.local_version} 更新成功！")
    return 0


if __name__ == "__main__":
    if file_io.update_config(os.path.join(ROOT_DIR, "config.ini")):
        sys.exit(1)
    init()
    app.update_interact(update)
