#!/usr/bin/python

import os
import settings
import math

from flask import render_template, request, redirect, url_for, flash, session
from git import Repo

from constants import LANGUAGES
from helpers import *

def index():
    return render_template('index.html')

def new():
    if 'user' not in session:
        return render_template('error', error='You need to be logged in to do that.')

    if request.method == 'GET':
        return render_template('edit.html', title='New Paste', message='Initial version', new=True, languages=LANGUAGES)
    else:
        # Check that all required fields are present.
        if not set(('title', 'message', 'language', 'content')).issubset(set(request.form.keys())):
            flash('Please fill in all fields', 'warning')
            return render_template('edit.html', new=True, languages=LANGUAGES, **request.form)

        # Get the next free ID.
        rid = max([int(f.replace('.deleted', '')) for f in os.listdir(settings.REPO_DIR)] + [0]) + 1

        # Create a new repo.
        repo = PasteRepo.init(rid)
        repo.language = LANGUAGES[request.form['language']]
        repo.mainfile = 'main' + repo.language['extensions'][0]

        # Set owner.
        cw = repo.config_writer('repository')
        cw.add_section('user')
        cw.set('user', 'name', session['user']['name'])
        cw.set('user', 'email', session['user']['email'])
        cw.write()

        # Commit.
        repo.update(request.form['message'], request.form['title'], request.form['content'])

        # Message.
        flash('Paste created', 'success')
        
        # View the paste.
        return redirect(url_for('view', rid=rid))

def list(page=1):
    # Get a list of all directory names.
    dirnames = [int(dirname) for dirname in os.listdir(settings.REPO_DIR) if not dirname.endswith('.deleted')]
    dirnames.sort()

    # Determine the number of pages.
    pages = math.ceil(len(dirnames) / settings.REPO_PER_PAGE)

    # Get the current page.
    dirnames = dirnames[settings.REPO_PER_PAGE * (page - 1):settings.REPO_PER_PAGE * page]
    repos = [PasteRepo(dirname) for dirname in dirnames]

    return render_template('list.html', repos=repos, page=page, pages=pages)

@fetch_repo()
def view(repo):
    content = repo.get_content()
    if 'renderer' in repo.language:
        content = repo.language['renderer'](content)
    
    return render_template('view/{}.html'.format(repo.language['view']), content=content, repo=repo)

@fetch_repo(require_owner=True)
def edit(repo):
    if request.method == 'GET':
        return render_template('edit.html', repo=repo)
    else:
        # Check that all required fields are present.
        if not set(('title', 'message', 'content')).issubset(set(request.form.keys())):
            flash('Please fill in all fields', 'warning')
            return render_template('edit.html', repo=repo, **request.form)

        # Commit.
        repo.update(request.form['message'], request.form['title'], request.form['content'])

        # Message.
        flash('Paste updated', 'success')

        # View the paste.
        return redirect(url_for('view', rid=rid))

@fetch_repo(require_owner=True)
def delete(repo):
    if request.method == 'GET':
        return render_template('delete.html', repo=repo)
    else:
        # Rename the directory.
        directory = repo.working_dir
        os.rename(directory, directory.rstrip('/\\') + '.deleted')

        # Message.
        flash('Paste deleted', 'success')

        # Go to the main page.
        return redirect(url_for('index'))

@fetch_repo()
def history(repo):
    return render_template('history.html', repo=repo)
