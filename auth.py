import urllib

from requests_oauthlib import OAuth2Session
from flask import request, session, redirect, url_for as uf, render_template, flash, g
from flask.json import jsonify

import settings
from constants import OAUTH_PROVIDERS

class User(object):
    """
    An user.

    Can be an anonymous user, or can be a logged in user.
    """

    def __init__(self):
        """
        Create a new user object.

        If there is user data in the Flask session this will be used.
        """
        if 'user' in session:
            self.login(session['user']['email'], session['user']['name'])
        else:
            self.logout()

    def login(self, email, name):
        """
        Login the user.
        """
        self.email = email
        self.name = name
        self._is_anon = False
        self._is_admin = email in settings.ADMINS
        session['user'] = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def logout(self):
        """
        Logout the user.
        """
        self.email = settings.ANONYMOUS_EMAIL
        self.name = settings.ANONYMOUS_NAME
        self._is_anon = True
        self._is_admin = False
        if 'user' in session:
            del session['user']

    def save(self):
        """
        Save the current user data in the session.
        """

    def is_anon(self):
        """
        Whether the user is an anonymous user.
        """
        return self._is_anon

    def is_admin(self):
        """
        Whether the user is an admin.
        """
        return self._is_admin
    
    def is_owner(self, repo):
        """
        Whether the user is owner of the repo.
        """
        try:
            assert self.email == repo.owner['email']
            return True
        except:
            return False

    def can_create(self):
        """
        Whether the user can create a new repo.
        """
        return not self.is_anon() or settings.ANONYMOUS_CREATE

    def can_edit(self, repo):
        """
        Whether the user can edit the repo.
        """
        return self.is_admin() or (self.is_owner(repo) and (not self.is_anon() or settings.ANONYMOUS_EDIT))

    def can_delete(self, repo):
        """
        Whether the user can delete the repo.
        """
        return self.is_admin() or (self.is_owner(repo) and (not self.is_anon() or settings.ANONYMOUS_DELETE))

def provide_user():
    """
    Get the user from the session, and insert it into all jinja templates.
    """
    g.user = User()

def provider_prop(key):
    """
    Get a property of the chosen provider.
    """
    return OAUTH_PROVIDERS[session['provider']][key]

def create_provider(*args, **kwargs):
    """
    Create an Oauth2Session.
    """
    # Create the base provider.
    provider = OAuth2Session(provider_prop('client_id'), 
                             *args,
                             redirect_uri=url_for('callback', _external=True),
                             state='oauth_state' in session and session['oauth_state'] or None,
                             **kwargs)

    # Register compliance hooks, if needed.
    try:
        for name, hook in provider_prop('compliance_hooks').items():
            provider.register_compliance_hook(name, hook)
    except KeyError:
        pass

    return provider

def url_for(*args, **kwargs):
    return uf(*args, **kwargs).replace('127.0.0.1:5000', 'pastegit.waxd.nl')

def login():
    if not g.user.is_anon():
        flash("You're logged in already.", 'info')
        return redirect(url_for('index'))

    if request.args.get('provider', '') in OAUTH_PROVIDERS:
        return _login_perform()
    else:
        return _login_pickprovider()

def _login_pickprovider():
    """
    Step 0: Selecting a provider.
    """
    return render_template('login.html', providers=OAUTH_PROVIDERS)

def _login_perform():
    """
    Step 1: User Authorization.
 
    Redirect the user/resource owner to the OAuth provider using an URL with a
    few key OAuth parameters.
    """

    # Get the provider of choice.
    session['provider'] = request.args.get('provider', '')

    # Build the request.
    provider = create_provider(scope=provider_prop('scope'))
    authorization_url, state = provider.authorization_url(provider_prop('auth_uri'))
 
    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state

    # Go to the authorization url.
    return redirect(authorization_url)
 
def callback():
    """
    Step 2: Retrieving an access token.
 
    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
 
    # Get the token.
    provider = create_provider()
    token = provider.fetch_token(provider_prop('token_uri'), 
                                 client_secret=provider_prop('client_secret'),
                                 authorization_response=request.url)
 
    # Store the token for later use.
    session['oauth_token'] = token

    # Get the user data.
    get_user_data()

    # Message.
    flash('You are now logged in', 'success')

    # Go back to the index page.
    return redirect(url_for('index'))

def get_user_data():
    """
    Step 3: Get the user data.

    Now that we're authenticated with our provider of choice, we can fetch the
    user data. We only need a few fields, and we discard the rest.
    """
    provider = OAuth2Session(provider_prop('client_id'), token=session['oauth_token'])
    userdata = provider.get(provider_prop('profile_uri')).json()
    g.user.login(userdata['email'], userdata['name'])

def logout():
    # Delete all auth-related stuff from the session.
    for key in ('oauth_state', 'oauth_token'):
        if key in session:
            del session[key]
    g.user.logout()

    # Message.
    flash('You are now logged out', 'success')
    
    return redirect(url_for('index'))

def test():
    provider = OAuth2Session(provider_prop('client_id'), token=session['oauth_token'])
    return jsonify(provider.get(provider_prop('profile_uri')).json())
