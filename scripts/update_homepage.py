#!/usr/bin/python
from __future__ import with_statement
import os
import sys
import sqlite3
import time

import sources
import settings
import traceback
from time import sleep

DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'activity.db')

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

def with_retries(retry_count, method, *args):
    success = False
    for i in range(0, retry_count):
        try:
            result = method(*args)
        except Exception as e:
            sleep(2 ** (i + 1))
            continue
        success = True
        break
    if success:
        return result
    else:
        raise Exception('%s failed after %d tries, most recent error: %s: "%s"' % 
            (method.__name__, retry_count, e.__class__.__name__, e))

def record_last_update(source_name):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('select count(*) from sources where source_name = ?', (source_name,))
    row_count = cur.fetchone()[0]
    cur.close()

    now = int(time.time())
    if row_count == 0:
        # insert
        print "insert"
        conn.execute('insert into sources (source_name, last_success_time) values (?, ?)', (source_name, now))
    else:
        # update
        print "update"
        conn.execute('update sources set last_success_time = ? where source_name = ?', (now, source_name))

    conn.commit()
    conn.close()

def record_last_error(source_name, error):
    conn = sqlite3.connect('activity.db')
    cur = conn.cursor()
    cur.execute('select count(*) from sources where source_name = ?', (source_name,))
    row_count = cur.fetchone()[0]
    cur.close()

    now = int(time.time())
    if row_count == 0:
        # insert
        print "insert"
        conn.execute('insert into sources (source_name, last_error_time, last_error_message) values (?, ?, ?)', (source_name, now, error))
    else:
        # update
        print "update"
        conn.execute('update sources set last_error_time = ?, last_error_message = ? where source_name = ?', (now, error, source_name))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Accept a list of sources to update on the command line.
    # If no args then update all.
    requested = sys.argv[1:] if len(sys.argv) > 1 else settings.SOURCES.keys()

    for source_name in requested:
        source = settings.SOURCES[source_name]
        file_name, method, args = source[0], getattr(sources, source[1]), source[2:]
        try:
            html = with_retries(5, method, *args)
            if html is None:
                raise Exception('None returned by method \'%s\' when HTML content expected' % method.__name__)
            write_file(file_name, html)
            record_last_update(source_name)
        except Exception as e:
            sys.stderr.write('An error occured processing \'%s\', update will continue with the next source\n' % source_name)
            traceback.print_exc(file = sys.stderr)
            record_last_error(source_name, traceback.format_exc())