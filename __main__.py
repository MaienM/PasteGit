#!/usr/bin/python

import os
import settings

from flask import Flask
from flask_bootstrap import Bootstrap

import core
import auth

# Create the app.
app = Flask(__name__)
app.secret_key = settings.FLASK_SECRET_KEY
Bootstrap(app)

# Bind the routes.
app.route('/')(core.index)
app.route('/new', methods=('GET', 'POST'))(core.new)
app.route('/list')(core.list)
app.route('/<rid>')(core.view)
app.route('/<rid>/<rev>')(core.view)
app.route('/<rid>/edit', methods=('GET', 'POST'))(core.edit)
app.route('/<rid>/delete', methods=('GET', 'POST'))(core.delete)

app.route('/login')(auth.login)
app.route('/logout')(auth.logout)
app.route('/callback')(auth.callback)
app.route('/test')(auth.test)

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('0.0.0.0', debug=True)

