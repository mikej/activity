import re
import feedparser
from utils import make_link, make_ul

def get_so_answers(user_id):
    f = feedparser.parse("http://stackoverflow.com/feeds/user/%s" % user_id)
    answers = [entry for entry in f.entries if is_answer(entry)]
    answers.sort(key = lambda e : e.published_parsed, reverse = True)
    if len(answers) > 0:
        items = []
        for answer in answers[:5]:
            items.append(make_link(get_question_title(answer), get_question_link(answer)))
        return make_ul(items)
    else:
        return "<p>No recent answers</p>"

def is_answer(e):
    return e.title.startswith('Answer by ')

def get_question_title(entry):
    m = re.match("^Answer by mikej for (.+)$", entry.title)
    if m:
        return m.group(1)
    else:
        raise Exception("Entry %s is not an answer to a question" % entry.title)

def get_question_link(entry):
    link = entry.link
    prefix = "http://stackoverflow.com,"
    return link[len(prefix):] if link.startswith(prefix) else link