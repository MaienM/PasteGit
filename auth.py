import urllib
from requests_oauthlib import OAuth2Session

from flask import request, session, redirect, url_for, render_template, flash
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

def _p(key):
    """
    Get a property of the chosen provider.
    """
    return OAUTH_PROVIDERS[session['provider']][key]

def login():
    if 'user' in session and not session['user']['is_anon']:
        flash("You're logged in already.", 'info')
        return redirect(url_for('index'))

    if request.args.get('provider', '') in OAUTH_PROVIDERS:
        return login_perform()
    else:
        return login_pickprovider()

def login_pickprovider():
    """
    Step 0: Selecting a provider.
    """
    return render_template('login.html', providers=OAUTH_PROVIDERS)

def login_perform():
    """
    Step 1: User Authorization.
 
    Redirect the user/resource owner to the OAuth provider using an URL with a
    few key OAuth parameters.
    """

    # Get the provider of choice.
    session['provider'] = request.args.get('provider', '')

    # Build the request.
    provider = OAuth2Session(_p('client_id'), 
                             redirect_uri=url_for('callback', _external=True),
                             scope=_p('scope'))
    authorization_url, state = provider.authorization_url(_p('auth_uri'))
 
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
 
    provider = OAuth2Session(_p('client_id'), state=session['oauth_state'])
    token = provider.fetch_token(_p('token_uri'), 
                                 client_secret=_p('client_secret'),
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
    provider = OAuth2Session(_p('client_id'), token=session['oauth_token'])
    userdata = provider.get(_p('profile_uri')).json()
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
    provider = OAuth2Session(_p('client_id'), token=session['oauth_token'])
    return jsonify(provider.get(_p('profile_uri')).json())
