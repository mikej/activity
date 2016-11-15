OUTPUT_DIR = '/Users/mike/Projects/josephson.org/htdocs/includes'

# map of source name to (file name, generating method, method args)
SOURCES = {
    'pinboard' : ('pinboard.html', 'get_pinboard', 'PINBOARD_API_KEY'),
    'last.fm' : ('last_fm.html', 'get_last_fm', 'LASTFM_USERNAME', 'LASTFM_KEY'),
    'goodreads' : ('goodreads.html', 'get_goodreads', 'GOODREADS_USERID', 'currently-reading'),
    'lanyrd' : ('lanyrd.html', 'get_lanyrd', 'LANYRD_USERNAME'),
    'so' : ('so.html', 'get_so_answers', 'STACKOVERFLOW_USERID'),
    'github' : ('github.html', 'get_github_activity', 'GITHUB_USERNAME')
}

HEALTH_CHECK_URL=None
