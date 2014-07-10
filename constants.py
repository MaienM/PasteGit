import json
import urlparse

import settings
from fixes import fb_access_token_response

# Languages in which pastes can be made.
LANGUAGES = {
    'python': {
        'name': 'Python',
        'extensions': ('.py',),
        'view': 'code',
    },
    'markdown': {
        'name': 'Markdown',
        'extensions': ('.md', '.markdown'),
        'view': 'markdown',
    }
}

# Filter out unwanted languages based on the settings file.
if settings.LANGUAGES_WHITELIST:
    for key in LANGUAGES.keys():
        if key not in settings.LANGUAGES_WHITELIST:
            del LANGUAGES[key]
if settings.LANGUAGES_BLACKLIST:
    for key in LANGUAGES.keys():
        if key in settings.LANGUAGES_WHITELIST:
            del LANGUAGES[key]


# OAuth providers.
OAUTH_PROVIDERS = {
    'google': {
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://accounts.google.com/o/oauth2/token',
        'profile_uri': 'https://www.googleapis.com/oauth2/v1/userinfo',
        'scope': ['https://www.googleapis.com/auth/userinfo.email'],
    },
    'facebook': {
        'auth_uri': 'https://www.facebook.com/dialog/oauth',
        'token_uri': 'https://graph.facebook.com/oauth/access_token',
        'profile_uri': 'https://graph.facebook.com/me',
        'scope': ['public_profile', 'email'],
        'compliance_hooks': {
            'access_token_response': fb_access_token_response,
        },
    },
}

# Read client secrets from the settings file.
for name in OAUTH_PROVIDERS.keys():
    if name not in settings.OAUTH_SECRETS:
        del OAUTH_PROVIDERS[name]
    else:
        OAUTH_PROVIDERS[name] = dict(OAUTH_PROVIDERS[name].items() + settings.OAUTH_SECRETS[name].items())
