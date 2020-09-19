#!/usr/bin/env python
import os
import sys

# Use dev settings if not otherwise configured.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    os.symlink('settings_dev.py', THIS_DIR+'/settings.py')
except OSError:
    pass

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
    sys.path.append(os.getcwd())
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
