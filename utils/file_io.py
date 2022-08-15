import configparser
import os
import shutil
import time
import zipfile
from subprocess import call

import requests
import win32api

CONFIG = {}


def send2trash(path):
    """https://pypi.org/project/Send2Trash"""
    from ctypes import Structure, addressof, byref, c_uint, create_unicode_buffer, windll
    from ctypes.wintypes import BOOL, HWND, LPCWSTR, UINT

    class SHFILEOPSTRUCTW(Structure):
        _fields_ = [
            ("hwnd", HWND),
            ("wFunc", UINT),
            ("pFrom", LPCWSTR),
            ("pTo", LPCWSTR),
            ("fFlags", c_uint),
            ("fAnyOperationsAborted", BOOL),
            ("hNameMappings", c_uint),
            ("lpszProgressTitle", LPCWSTR),
        ]

    shell32 = windll.shell32
    SHFileOperationW = shell32.SHFileOperationW
    FO_MOVE = 1
    FO_COPY = 2
    FO_DELETE = 3
    FO_RENAME = 4
    FOF_MULTIDESTFILES = 1
    FOF_SILENT = 4
    FOF_NOCONFIRMATION = 16
    FOF_ALLOWUNDO = 64
    FOF_NOERRORUI = 1024

    fileop = SHFILEOPSTRUCTW()
    fileop.hwnd = 0
    fileop.wFunc = FO_DELETE
    buffer = create_unicode_buffer(path, len(path) + 2)
    fileop.pFrom = LPCWSTR(addressof(buffer))
    fileop.pTo = None
    fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_NOERRORUI | FOF_SILENT
    fileop.fAnyOperationsAborted = 0
    fileop.hNameMappings = 0
    fileop.lpszProgressTitle = None
    result = SHFileOperationW(byref(fileop))
    return result  # 0 means success


def read_config(path) -> dict:
    # 路径合法性检测
    if not os.path.isfile(path):
        print(f"配置文件不存在：{path}")
        return {}
    config = configparser.ConfigParser()
    config.optionxform = str  # key case sensitive
    try:
        config.read(path, encoding="utf-8")
    except Exception as e:
        print(e)
        print(f"配置文件有误：{path}")
        return {}
    return config._sections


def update_config(path):
    global CONFIG
    CONFIG = read_config(path)
    if not CONFIG:
        return -1
    # 将proxy配置项转换为字典格式
    if "common" in CONFIG and "proxy" in CONFIG["common"] and CONFIG["common"]["proxy"]:
        CONFIG["common"]["proxy_dict"] = {
            "http": CONFIG["common"]["proxy"],
            "https": CONFIG["common"]["proxy"],
        }
    else:
        CONFIG["common"]["proxy_dict"] = {}
    return 0


def get_config(section, key, default="", verbose=True):
    global CONFIG
    if section in CONFIG:
        return CONFIG[section].get(key, default)
    else:
        if verbose:
            print(f"配置文件中 {section} 项不存在！")
        return ""


def terminate_process(name, verbose=False):
    tasklist = "".join(os.popen(f'tasklist /FI "IMAGENAME eq {name}"').readlines())
    if "PID" in tasklist:  # 进程存在
        if verbose:
            while True:
                print(f"{name} 正在运行，是否结束进程？(Y/N) ", end="")
                choice = input().upper()
                if choice == "N":
                    return
                elif choice == "Y":
                    break
                else:
                    continue
        os.system(f'taskkill /F /IM "{name}"')


def get_exe_version(path):
    # 路径合法性检测
    if not os.path.isfile(path):
        print(f"目标文件不存在：{path}")
        return "0.0.0.0"

    try:
        info = win32api.GetFileVersionInfo(path, os.sep)
    except Exception as e:
        print(e)
        return "0.0.0.0"

    ms = info["FileVersionMS"]
    ls = info["FileVersionLS"]
    version = "{}.{}.{}.{}".format(win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls), win32api.LOWORD(ls))
    return version


def cut_dir(src_dir, dest_dir, remove_old_dir=True):
    # 路径合法性检测
    if not os.path.isdir(src_dir):
        print(f"源目录不存在：{src_dir}")
        return -1
    if not os.path.isdir(dest_dir):
        print(f"目标目录不存在：{dest_dir}")
        return -1

    for item in os.listdir(src_dir):
        full_path = os.path.join(src_dir, item)
        shutil.move(full_path, dest_dir)
    if remove_old_dir:
        # shutil.rmtree(src_path)
        os.removedirs(src_dir)
    return 0


def downloader(url, file_path, proxy_dict: dict = None, verbose=True):
    # 路径合法性检测
    dest_dir = os.path.dirname(file_path)
    if not os.path.exists(dest_dir):
        print(f"目标目录不存在：{dest_dir}")
        return -1
    if os.path.isdir(file_path):
        print("目标路径错误！请输入文件路径，而非目录")
        return -1
    if proxy_dict is None:
        proxy_dict = {}
    if verbose:
        if os.path.isfile(file_path):
            while True:
                print("目标文件已存在，是否覆盖？(Y/N) ", end="")
                input_confirm = input().upper()
                if input_confirm == "N":
                    while True:
                        print("是否直接使用已存在的文件？(Y/N) ", end="")
                        input_confirm2 = input().upper()
                        if input_confirm2 == "N":
                            return -1
                        elif input_confirm2 == "Y":
                            return 0
                        else:
                            continue
                elif input_confirm == "Y":
                    break
                else:
                    continue

    # https://blog.csdn.net/programmer_yf/article/details/80512428
    size = 0  # 已下载文件大小
    chunk_size = 1024  # 每次下载1024b
    try:
        file_response = requests.get(url, stream=True, proxies=proxy_dict, timeout=10)
    except:
        print("下载链接请求失败！")
        return -1
    if file_response.status_code == requests.codes.ok:
        start_time = time.time()
        print("下载链接请求成功，即将开始下载！")
        try:
            file_size = int(file_response.headers["content-length"])
        except KeyError:
            print("下载链接有误！")
            return -1
        except Exception as e:
            print(e)
            return -1
        if file_response.status_code == requests.codes.ok:
            print("[文件大小]: {:0.2f} MB".format(file_size / chunk_size / 1024))
            with open(file_path, "wb") as f:
                for data in file_response.iter_content(chunk_size=chunk_size):
                    f.write(data)
                    size += len(data)
                    # 进度条
                    if verbose:
                        print(
                            "\r"
                            + "[下载进度]: {}{:.2f}%".format(
                                ">" * int(size * 50 / file_size), float(size / file_size * 100)
                            ),
                            end="",
                        )
                    else:  # 避免过于频繁的print
                        percent = float(size / file_size * 100)
                        # 百分比为整十（精确到小数点后1位）才会print，且避免重复
                        percent_10x = int(percent * 10)
                        if "percent_10x_last" not in dir():  # 未定义变量（第一次循环）
                            percent_10x_last = -1
                        if percent_10x % 100 == 0 and percent_10x != percent_10x_last:
                            print("\r" + "[下载进度]: {}{:.2f}%".format(">" * int(size * 50 / file_size), percent), end="")
                            percent_10x_last = percent_10x

        end_time = time.time()
        print("")
        print("下载完成！用时 {:.2f} 秒".format(end_time - start_time))
        return 0
    else:
        print(f"下载链接请求失败！响应状态码：{file_response.status_code}")
        return -1


def downloader_idm(exe_path, url, file_path):
    # 路径合法性检测
    dest_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    if not os.path.exists(dest_dir):
        print(f"目标目录不存在：{dest_dir}")
        return -1
    if os.path.isdir(file_path):
        print("目标路径错误！请输入文件路径，而非目录")
        return -1
    if not os.path.exists(exe_path):
        print("IDMan.exe 不存在！")
        return -1

    # 先结束已存在的IDM进程，否则下载命令可能会出错
    terminate_process("idman.exe")
    call([exe_path, "/d", url, "/p", dest_dir, "/f", file_name, "/n", "/q"])
    # call([exe_path, "/s"])
    return 0


def unpack_zip(file_path, dest_dir):
    # 路径合法性检测
    if not os.path.exists(dest_dir):
        print(f"目标目录不存在：{dest_dir}")
        return -1

    try:
        zfile = zipfile.ZipFile(file_path, "r")
        zfile.extractall(path=dest_dir)
        zfile.close()
        print("解压成功！")
    except FileNotFoundError:
        print(f"文件不存在：{file_path}")
        return -1
    except zipfile.BadZipFile:
        print(f"文件损坏：{file_path}")
        return -1
    except Exception as e:
        print(e)
        return -1
    return 0


def unpack_7z(exe_path, file_path, dest_dir):
    # 路径合法性检测
    if not os.path.exists(dest_dir):
        print(f"目标目录不存在：{dest_dir}")
        return -1
    if not os.path.exists(exe_path):
        print("7z.exe 不存在！")
        return -1

    # cmd = f'exe_path x "{file_path}" -o"{dest_dir}"'
    # os.system(cmd)
    call([exe_path, "x", file_path, "-o" + dest_dir])
    print("解压完成！")
    return 0


def empty_dir(dir_path, to_trash=False, whitelist: list = None):
    # 路径合法性检测
    if not os.path.isdir(dir_path):
        print(f"目标目录不存在：{dir_path}")
        return -2

    if whitelist is None:
        whitelist = []

    if to_trash:
        if whitelist:
            tmp_dir = os.path.join(os.environ.get("TEMP"), f"updater_whitelist_{os.path.basename(dir_path)}")
            os.mkdir(tmp_dir)
            for item in os.listdir(dir_path):
                if item in whitelist:
                    shutil.move(os.path.join(dir_path, item), os.path.join(tmp_dir, item))
        if send2trash(dir_path):
            print(f"无法删除：{dir_path}")
        else:
            os.mkdir(dir_path)
            if whitelist:
                cut_dir(tmp_dir, dir_path)
    else:
        for item in os.listdir(dir_path):
            if item in whitelist:
                continue
            full_path = os.path.join(dir_path, item)
            # full_path = full_path.replace("\\", "/")
            if os.path.isdir(full_path):
                try:
                    shutil.rmtree(full_path)
                except Exception as e:
                    print(f"无法删除：{full_path}")
                    print(e)
            else:
                try:
                    os.remove(full_path)
                except Exception as e:
                    print(f"无法删除：{full_path}")
                    print(e)
    now_list = os.listdir(dir_path)
    if now_list and (not set(now_list).issubset(set(whitelist))):
        print("某些文件无法删除！")
        return -1
    else:
        print(f"已清空：{dir_path}")
        if whitelist:
            print("忽略：", end="")
            print(whitelist)
        return 0


def empty_dir_interact(dir_path, to_trash=False, whitelist: list = None, verbose=True):
    if whitelist is None:
        whitelist = []
    if verbose:
        while True:
            print(f'是否清空"{dir_path}"？(Y/N) ', end="")
            input_confirm = input().upper()
            if input_confirm == "N":
                return -1
            elif input_confirm == "Y":
                break
            else:
                continue
        while True:
            result = empty_dir(dir_path, to_trash, whitelist)
            if result == -1:
                while True:
                    print("是否重试？(Y/N) ", end="")
                    input_retry = input().upper()
                    if input_retry == "N":
                        return -1
                    elif input_retry == "Y":
                        break
                    else:
                        continue
            else:
                return 0
    else:
        return empty_dir(dir_path, to_trash, whitelist)
