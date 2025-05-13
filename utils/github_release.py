import json
import os

import requests

GITHUB_API = "https://api.github.com"


def _version_compare(a: str, b: str, split="."):
    """
    a > b: 1
    a < b: -1
    a = b: 0
    """
    a = "".join(list(filter(lambda x: x in f"0123456789{split}", a)))
    b = "".join(list(filter(lambda x: x in f"0123456789{split}", b)))
    a_list = list(map(int, list(filter(str.isdigit, a.split(split)))))
    b_list = list(map(int, list(filter(str.isdigit, b.split(split)))))
    diff = len(a_list) - len(b_list)
    if diff > 0:
        b_list.extend([0] * diff)
    elif diff < 0:
        a_list.extend([0] * (0 - diff))

    for i in range(len(a_list)):
        if a_list[i] != b_list[i]:
            return 1 if a_list[i] > b_list[i] else -1
    return 0


def oauth_test(oauth_token: str, proxy_dict: dict = None):
    """
    0: OAuth ok
    1: no OAuth
    -1: failed
    """
    api = f"{GITHUB_API}/rate_limit"
    headers = {"Authorization": f"token {oauth_token}"}
    if proxy_dict is None:
        proxy_dict = {}
    try:
        response = requests.get(api, headers=headers, allow_redirects=False, proxies=proxy_dict, timeout=10)
    except requests.exceptions.ReadTimeout:
        print("Request timeout")
        return -1
    except Exception as e:
        print(e)
        return -1
    if response.status_code == requests.codes.ok:
        json_dict = json.loads(response.content)
        limit = json_dict["resources"]["core"]["limit"]
        return 0 if int(limit) >= 5000 else 1
    else:
        print(f"Request failed: {response.status_code}")
        return -1


class GitHubRelease:
    local_dir = ""
    exe_path = ""
    local_version = ""

    repo = ""
    repo_url = ""
    release_file_name = ""

    latest_version = ""
    release_assets = []
    release_body = ""
    release_file_url = ""

    version_str_processor = None

    def __init__(self, repo: str):
        self.repo = repo
        self.repo_url = f"https://github.com/{repo}"

    def check_release(self, include_pre=False, proxy_dict: dict = None, oauth_token=""):
        api = f"{GITHUB_API}/repos/{self.repo}/releases"
        headers = {"Authorization": f"token {oauth_token}"} if oauth_token else {}
        if not include_pre:
            api += "/latest"
        if proxy_dict is None:
            proxy_dict = {}
        try:
            response = requests.get(api, headers=headers, allow_redirects=False, proxies=proxy_dict, timeout=10)
        except requests.exceptions.ReadTimeout:
            print("Request timeout")
            return
        except Exception as e:
            print(e)
            return
        if response.status_code == requests.codes.ok:
            json_dict = json.loads(response.content)
            if isinstance(json_dict, list):
                json_dict = json_dict[0]
            self.latest_version = json_dict["tag_name"]
            self.release_assets: "list[dict[str, str]]" = json_dict["assets"]
            self.release_body = json_dict["body"]
            if self.release_file_name:
                self.release_file_url = self.get_download_url()
        else:
            print(f"Request failed: {response.status_code}")

    def print_assets(self):
        for item in self.release_assets:
            print(item["name"], end="\t")
            print(" | ", end="")
            print("{:.2f} MB".format(int(item["size"]) / 1024 / 1024))

    def get_download_url_by(self, value, key="name"):
        for item in self.release_assets:
            if item[key] == value:
                return item["browser_download_url"]
        return ""

    def get_download_url(self, fuzzy=False, version_replace=False, placeholder="$", keep_v=False):
        if fuzzy:  # 实际版本号与文件名并不总是一致，可以采用模糊查找
            release_file_name_prefix, release_file_name_suffix = self.release_file_name.split(placeholder, 1)
            for item in self.release_assets:
                filename = item["name"]
                if filename.startswith(release_file_name_prefix) and filename.endswith(release_file_name_suffix):
                    self.release_file_name = filename
                    return item["browser_download_url"]
            return ""
        else:
            if version_replace:  # Release 文件名包含版本号，在配置文件中用符号代替
                assert not fuzzy, "模糊查找与版本号替换不能同时使用！"
                latest_version = self.latest_version
                if latest_version.startswith("v") and not keep_v:
                    latest_version = latest_version[1:]
                self.release_file_name = self.release_file_name.replace(placeholder, latest_version)
            return self.get_download_url_by(self.release_file_name, "name")

    def is_latest(self, verbose=False):
        if not self.local_version:
            if verbose:
                print("本地版本号不存在，无法进行版本比对！")
            return -1
        if not self.latest_version:
            if verbose:
                print("最新版本号不存在，无法进行版本比对！")
            return -2
        if self.version_str_processor is None:
            diff = _version_compare(self.local_version, self.latest_version)
        else:
            diff = _version_compare(
                self.version_str_processor(self.local_version), self.version_str_processor(self.latest_version)
            )
        if diff == 0:
            if verbose:
                print("已为最新版本！")
            return 1
        elif diff > 0:
            if verbose:
                print("本地版本高于最新版本！")
            return 1
        else:
            if verbose:
                print("非最新版！")
                print(f"最新版本：{self.latest_version}")
                print("Release 文件如下：")
                print("-" * 40)
                self.print_assets()
                print("-" * 40)
                if self.release_file_url:
                    print(f"其中 {self.release_file_name} 的下载链接为：")
                    print(self.release_file_url)
                else:
                    print(f"未找到指定的 Release 文件！（{self.release_file_name}）")
            return -2 if not self.release_file_url else 0

    def update_interact(self, update):
        print(f"本地版本：{self.local_version}")
        if self.is_latest(verbose=True) == 0:
            while True:
                print("是否下载更新？(Y/N) ", end="")
                choice = input().upper()
                if choice == "N":
                    break
                elif choice == "Y":
                    if not update():
                        break
