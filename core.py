#!/usr/bin/python

import os
import settings

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
        rid = max([int(f.replace('.deleted', '')) for f in os.listdir(settings.REPODIR)] + [0]) + 1

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
        
        # View the paste.
        return redirect(url_for('view', rid=rid))

def list():
    repos = []
    for dirname in os.listdir(settings.REPODIR):
        if dirname.endswith('.deleted'):
            continue
        try:
            with open(os.path.join(settings.REPODIR, dirname, 'title'), 'r') as f:
                repos.append({
                    'id': int(dirname),
                    'title': f.read(),
                })
        except:
            pass
    repos.sort(key=lambda x: x['id'])
    return render_template('list.html', repos=repos)

@fetch_repo
def view(repo, rev='HEAD'):
    content = repo.get_content()
    if 'renderer' in repo.language:
        content = repo.language['renderer'](content)
    
    return render_template('view/{}.html'.format(repo.language['view']), content=content, repo=repo)

@fetch_repo
@require_repo_owner
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

        # View the paste.
        return redirect(url_for('view', rid=rid))

@fetch_repo
@require_repo_owner
def delete(repo):
    if request.method == 'GET':
        return render_template('delete.html', repo=repo)
    else:
        # Rename the directory.
        directory = repo.working_dir
        os.rename(directory, directory.rstrip('/\\') + '.deleted')

        # Go to the main page.
        return redirect(url_for('index'))

@fetch_repo
def history(repo):
    return render_template('history.html', repo=repo)
