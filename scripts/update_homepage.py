#!/usr/bin/python
from __future__ import with_statement
import os
import sys

import sources
import settings

def write_file(base_filename, content):
    filename = os.path.join(settings.OUTPUT_DIR, base_filename)
    filename_old = os.path.join(settings.OUTPUT_DIR, base_filename + ".old")
    filename_new = os.path.join(settings.OUTPUT_DIR, base_filename + ".new")
    current_file_exists = os.path.isfile(filename)

    if current_file_exists:
        with open(filename, "r") as f:
            old_content = unicode(f.read(), "utf-8")
        if old_content == content:
            return

    with open(filename_new, "w") as f:
        f.write(content.encode('utf-8'))

    if current_file_exists:
        if os.path.isfile(filename_old):
            os.remove(filename_old)
        os.rename(filename, filename_old)
    os.rename(filename_new, filename)

if __name__ == '__main__':
    # Accept a list of sources to update on the command line.
    # If no args then update all.
    requested = sys.argv[1:] if len(sys.argv) > 1 else settings.SOURCES.keys()

    for source_name in requested:
	source = settings.SOURCES[source_name]
	file_name, method, args = source[0], getattr(sources, source[1]), source[2:]
        html = method(*args)
        write_file(file_name, html)
