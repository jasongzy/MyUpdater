import sys
from time import sleep

import utils.file_io as file_io
from apps import app_dict

if file_io.update_config("./config.ini"):
    sys.exit(1)

for item in app_dict.values():
    # assert isinstance(item.app, GitHubRelease)
    with file_io.HiddenPrints():
        item.init(check_release=False)
    print(item.app.repo)
    item.init()
    item.app.update_interact(item.update)
    print("*" * 50)
    sleep(0.3)
