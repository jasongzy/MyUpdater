import os
import pkgutil
from importlib import import_module

app_dict = {
    name: import_module(f"{os.path.basename(os.path.dirname(__file__))}.{name}")
    for _, name, _ in pkgutil.iter_modules([os.path.dirname(__file__)])
}
