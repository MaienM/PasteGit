import urllib

from requests_oauthlib import OAuth2Session
from flask import request, session, redirect, url_for as uf, render_template, flash
from flask.json import jsonify

import settings
from constants import OAUTH_PROVIDERS

def anonymous():
    """
    If not logged in and ANONYMOUS is on, log in as anonymous.
    If logged in as anonymous and ANONYMOUS is off, log out.
    """
    if settings.ANONYMOUS:
        if 'user' not in session:
            session['user'] = {
                'email': 'test@example.com',
                'name': 'Anonymous',
                'is_anon': True,
            }
    else:
        if 'user' in session and session['user']['is_anon']:
            del session['user']

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
    if 'user' in session and not session['user']['is_anon']:
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
    print(userdata)
    session['user'] = {}
    session['user']['email'] = userdata['email']
    session['user']['name'] = userdata['name']
    session['user']['is_anon'] = False

def logout():
    # Delete all auth-related stuff from the session.
    for key in ('oauth_state', 'oauth_token', 'user'):
        if key in session:
            del session[key]

    # Message.
    flash('You are now logged out', 'success')
    
    return redirect(url_for('index'))

def test():
    provider = OAuth2Session(provider_prop('client_id'), token=session['oauth_token'])
    return jsonify(provider.get(provider_prop('profile_uri')).json())
