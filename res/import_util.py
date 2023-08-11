import sys
from os.path import abspath
from importlib import import_module


def import_by_file(module_name, module_path):
   module_path = abspath(module_path)
   sys_path = sys.path.copy()
   sys.path = [module_path] + sys.path
   module = import_module(module_name)
   sys.path = sys_path
   return module
