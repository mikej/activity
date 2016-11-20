import re
import feedparser
from utils import make_link, make_ul

def get_github_activity(user):
    f = feedparser.parse("http://github.com/%s.atom" % user)
    entries = f.entries
    entries.sort(key = lambda e : e.published_parsed, reverse = True)
    if len(entries) > 0:
        items = []
        for entry in entries[:5]:
            title = re.sub("^%s " % user, "", entry.title).capitalize()
            items.append(make_link(title, entry.link))
        return make_ul(items)
    else:
        return "<p>No recent activity</p>"