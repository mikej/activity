OUTPUT_DIR = '/Users/mike/Projects/josephson.org/htdocs/includes'

# map of source name to (file name, generating method, method args)
SOURCES = {
    'pinboard' : ('pinboard.html', 'bookmarks.get_pinboard', 'PINBOARD_API_KEY'),
    'last.fm' : ('last_fm.html', 'last_fm.get_last_fm', 'LASTFM_USERNAME', 'LASTFM_KEY'),
    'goodreads' : ('goodreads.html', 'goodreads.get_goodreads', 'GOODREADS_USERID', 'currently-reading'),
    'lanyrd' : ('lanyrd.html', 'lanyrd.get_lanyrd', 'LANYRD_USERNAME'),
    'so' : ('so.html', 'stackoverflow.get_so_answers', 'STACKOVERFLOW_USERID'),
    'github' : ('github.html', 'github.get_github_activity', 'GITHUB_USERNAME')
}

HEALTH_CHECK_URL=None
