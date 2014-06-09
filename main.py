#!/usr/bin/python

import os
import settings
import logging

from flask import Flask
from flask_bootstrap import Bootstrap

import core
import auth
import helpers

# Create the app.
app = Flask(__name__)
app.secret_key = settings.FLASK_SECRET_KEY
Bootstrap(app)

# Bind special functions.
app.before_request(auth.anonymous)

# Bind the routes.
app.route('/')(core.index)
app.route('/new', methods=('GET', 'POST'))(core.new)
app.route('/list')(core.list)
app.route('/<rid>')(core.view)
app.route('/<rid>/<rev>')(core.view)
app.route('/<rid>/edit', methods=('GET', 'POST'))(core.edit)
app.route('/<rid>/delete', methods=('GET', 'POST'))(core.delete)
app.route('/<rid>/history')(core.history)

app.route('/login')(auth.login)
app.route('/logout')(auth.logout)
app.route('/callback')(auth.callback)
app.route('/test')(auth.test)

# Bind the filters.
app.template_filter('timedelta')(helpers.timedelta)

# We don't have an SSL certificate yet.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Logging.
handler = logging.FileHandler('/var/www/pastegit/log')
handler.setLevel(logging.WARNING)
app.logger.addHandler(handler)

# Run with the built-in server if ran directly.
if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
