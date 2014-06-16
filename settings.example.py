# If you don't have an SSL certificate, set this to true.
ALLOW_INSECURE_AUTH = False

# The directory where repositories are stored.
REPO_DIR = '/absolute/path/to/repos'

# The amount of repositories per page.
REPO_PER_PAGE = 10

# Whether to allow anonymous users to create pastes.
ANONYMOUS_CREATE = False

# Whether to allow editing of anonymous pastes.
# This means that ANYONE can edit a paste made by an anonymous user.
ANONYMOUS_EDIT = False

# Same, but for deletion.
ANONYMOUS_DELETE = False

# The author of anonymous pastes.
ANONYMOUS_NAME = 'Anonymous'
ANONYMOUS_EMAIL = 'anon@waxd.nl'

# An list of email addresses for admins. When logged in with one of these you
# will have admin access, which means you can edit/delete any paste.
ADMINS = ()

# Language whitelist. If you set this to a list of language names, only those will be available.
LANGUAGES_WHITELIST = None

# Language blacklist. If you set this to a list of language names, all except for those will be available.
LANGUAGES_BLACKLIST = None

# The secret key of flask.
# See http://flask.pocoo.org/docs/quickstart/#sessions
FLASK_SECRET_KEY = ''

# Provider secrets. If you don't want to use a certain provider, simply remove
# it here.
OAUTH_SECRETS = {
    # See https://console.developers.google.com/
    'google': {
        'client_id': '',
        'client_secret': '',
    },

    # See https://developers.facebook.com/apps
    'facebook': {
        'client_id': '',
        'client_secret': '',
    },
}

