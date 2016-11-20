import feedparser
from utils import make_link, make_ul

def get_goodreads(id, shelf):
    f = feedparser.parse("http://www.goodreads.com/review/list_rss/%s?shelf=%s" % (id, shelf))
    items = []
    for entry in f.entries:
        items.append(make_link(entry.title, "http://www.goodreads.com/book/show/%s" % (entry.book_id)) + " by " + entry.author_name)
    return make_ul(items)