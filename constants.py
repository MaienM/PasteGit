import markdown

import settings

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
        'renderer': markdown.markdown,
    }
}

# OAuth providers.
OAUTH_PROVIDERS = {
    'google': {
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://accounts.google.com/o/oauth2/token',
        'profile_uri': 'https://www.googleapis.com/oauth2/v1/userinfo',
        'scope': ['https://www.googleapis.com/auth/userinfo.email'],
    },
    'github': {
        'auth_uri': 'https://github.com/login/oauth/authorize',
        'token_uri': 'https://github.com/login/oauth/access_token',
        'profile_uri': 'https://api.github.com/user',
        'scope': ['user.email'],
    },
    'facebook': {
        'auth_uri': 'https://www.facebook.com/dialog/oauth',
        'token_uri': 'https://graph.facebook.com/oauth/access_token',
        'profile_uri': 'https://graph.facebook.com/user/me',
        'scope': ['public_profile', 'email'],
    },
}
for name in OAUTH_PROVIDERS.keys():
    if name not in settings.OAUTH_SECRETS:
        del OAUTH_PROVIDERS[name]
    else:
        OAUTH_PROVIDERS[name] = dict(OAUTH_PROVIDERS[name].items() + settings.OAUTH_SECRETS[name].items())
