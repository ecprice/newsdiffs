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
    project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    print('Appending {} to sys.path'.format(project_dir))
    sys.path.append(project_dir)
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
