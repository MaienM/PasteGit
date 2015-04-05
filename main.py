#!/usr/bin/python

import os
import logging

from flask import Flask

from pastegit import core
from pastegit import auth
from pastegit import timer
from pastegit import filters
import settings

# Create the app.
app = Flask(__name__)
app.secret_key = settings.FLASK_SECRET_KEY

# Bind special functions.
app.before_request(timer.start)
app.after_request(timer.end)
app.before_request(auth.provide_user)

# Bind filters for the templates. 
for _filter in filters.FILTERS:
    app.template_filter(_filter.__name__)(_filter)

# Bind the routes.
app.route('/')(core.index)
app.route('/new', methods=('GET', 'POST'))(core.new)
app.route('/list')(core.list)
app.route('/list/<int:page>')(core.list)
app.route('/<rid>')(core.view)
app.route('/<rid>/<rev>')(core.view)
app.route('/<rid>/edit', methods=('GET', 'POST'))(core.edit)
app.route('/<rid>/delete', methods=('GET', 'POST'))(core.delete)
app.route('/<rid>/history')(core.history)
app.route('/<rid>/history/<rev>')(core.history)
app.route('/<rid>/releases', methods=('GET', 'POST'))(core.releases)
app.route('/<rid>/releases/<rev>', methods=('GET', 'POST'))(core.releases)

app.route('/login')(auth.login)
app.route('/logout')(auth.logout)
app.route('/callback')(auth.callback)

# Logging.
handler = logging.FileHandler('/var/www/pastegit/log')
handler.setLevel(logging.WARNING)
app.logger.addHandler(handler)

# Apply certain settings.
if settings.ALLOW_INSECURE_AUTH:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Run with the built-in server if ran directly.
if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
