#!/usr/bin/python

import os
import sys
import sqlite3
import time

DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'activity.db')

def get_stale_sources():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    threshold = int(time.time()) - (24 * 60 * 60) # 1 day ago
    cur.execute('select source_name, last_error_message, last_error_time from sources where last_success_time is null or last_success_time < ?', (threshold,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

stale_sources = get_stale_sources()

if len(stale_sources) > 0:
    print "Heads up! The following activity sources haven't updated in the last day:\n"
    for source in stale_sources:
        print source[0]