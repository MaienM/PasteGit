# The directory where repositories are stored.
REPODIR = 'repos'

# The secret key of flask.
# See http://flask.pocoo.org/docs/quickstart/#sessions
FLASK_SECRET_KEY = ''

# Language whitelist. If you set this to a list of language names, only those will be available.
LANGUAGES_WHITELIST = None

# Language blacklist. If you set this to a list of language names, all except for those will be available.
LANGUAGES_BLACKLIST = None

# Provider secrets. If you don't want to use a certain provider, simply remove
# it here.
OAUTH_SECRETS = {
    # See https://console.developers.google.com/
    'google': {
        'client_id': '',
        'client_secret': '',
    },

    # See https://github.com/settings/applications
    'github': {
        'client_id': '',
        'client_secret': '',
    },

    # See https://developers.facebook.com/apps
    'facebook': {
        'client_id': '',
        'client_secret': '',
    },
}

