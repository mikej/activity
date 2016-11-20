#!/usr/bin/python

import os
import sys
import sqlite3
import time
from datetime import datetime

import settings

DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'activity.db')

# http://www.siafoo.net/snippet/89
def age(from_date, since_date = None, target_tz=None, include_seconds=False):

    if from_date is None:
        return 'Never'

    if since_date is None:
        since_date = datetime.now(target_tz)

    distance_in_time = since_date - from_date
    distance_in_seconds = int(round(abs(distance_in_time.days * 86400 + distance_in_time.seconds)))
    distance_in_minutes = int(round(distance_in_seconds/60))

    if distance_in_minutes <= 1:
        if include_seconds:
            for remainder in [5, 10, 20]:
                if distance_in_seconds < remainder:
                    return "less than %s seconds" % remainder
            if distance_in_seconds < 40:
                return "half a minute"
            elif distance_in_seconds < 60:
                return "less than a minute"
            else:
                return "1 minute"
        else:
            if distance_in_minutes == 0:
                return "less than a minute"
            else:
                return "1 minute"
    elif distance_in_minutes < 45:
        return "%s minutes" % distance_in_minutes
    elif distance_in_minutes < 90:
        return "about 1 hour"
    elif distance_in_minutes < 1440:
        return "about %d hours" % (round(distance_in_minutes / 60.0))
    elif distance_in_minutes < 2880:
        return "1 day"
    elif distance_in_minutes < 43220:
        return "%d days" % (round(distance_in_minutes / 1440))
    elif distance_in_minutes < 86400:
        return "about 1 month"
    elif distance_in_minutes < 525600:
        return "%d months" % (round(distance_in_minutes / 43200))
    elif distance_in_minutes < 1051200:
        return "about 1 year"
    else:
        return "over %d years" % (round(distance_in_minutes / 525600))

def get_stale_sources():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    threshold = int(time.time()) - (24 * 60 * 60) # 1 day ago
    cur.execute('select source_name, last_error_message, last_error_time, last_success_time from sources where last_success_time is null or last_success_time < ?', (threshold,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

# only care about active sources i.e. ones still listed in settings.SOURCES
stale_sources = [stale_source for stale_source in get_stale_sources() if stale_source[0] in settings.SOURCES.keys()]

if len(stale_sources) > 0:
    sys.stderr.write("Heads up! The following activity sources haven't updated in the last day:\n\n")
    logs = ["Source: " + source[0] + ". Last success: " +
        age(None if source[3] is None else datetime.fromtimestamp(source[3])) +
        "\nMost recent error " + age(datetime.fromtimestamp(source[2])) + " ago: " + source[1] for source in stale_sources]
    sys.stderr.write("\n------------------------------------------------------------------------\n".join(logs))
