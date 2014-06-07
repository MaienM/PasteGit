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
        rid = max([int(f) for f in os.listdir(settings.REPODIR)] + [0]) + 1

        # Create a new repo.
        directory = os.path.join(settings.REPODIR, str(rid))
        repo = Repo.init(directory)

        # Set owner.
        cw = repo.config_writer('repository')
        cw.add_section('user')
        cw.set('user', 'name', session['user']['name'])
        cw.set('user', 'email', session['user']['email'])
        cw.write()
        
        # Write the title to a file.
        with open(os.path.join(directory, 'title'), 'w') as f:
            f.write(request.form['title'])

        # Write the paste to a file.
        mainfile = 'main' + LANGUAGES[request.form['language']]['extensions'][0]
        with open(os.path.join(directory, mainfile), 'w') as f:
            f.write(request.form['content'])

        # Commit the file.
        repo.index.add(['title', mainfile])
        repo.index.write()
        repo.index.commit(request.form['message'])

        # View the paste.
        return redirect(url_for('view', rid=rid))

def list():
    return render_template('list.html')

@route_fetch_repo
def view(rid, repo, rev='HEAD'):
    directory = repo.working_dir
    mainfile = get_repo_files(repo)[0]
    title = read_file(os.path.join(directory, 'title'))
    content = read_file(os.path.join(directory, mainfile))
    lang = detect_language(mainfile)

    if 'renderer' in lang:
        content = lang['renderer'](content)
    
    return render_template('view/{}.html'.format(lang['view']), title=title, content=content, rid=rid, repo_owner=we_repo_owner(repo))

@route_fetch_repo
@require_repo_owner
def edit(rid, repo):
    directory = repo.working_dir
    mainfile = get_repo_files(repo)[0]
    if request.method == 'GET':
        title = read_file(os.path.join(directory, 'title'))
        content = read_file(os.path.join(directory, mainfile))
        return render_template('edit.html', title=title, content=content, rid=rid, repo_owner=we_repo_owner(repo))
    else:
        # Check that all required fields are present.
        if not set(('message', 'content')).issubset(set(request.form.keys())):
            flash('Please fill in all fields', 'warning')
            return render_template('edit.html', rid=rid, repo_owner=we_repo_owner(repo), **request.form)

        # Write the paste to a file.
        with open(os.path.join(directory, mainfile), 'w') as f:
            f.write(request.form['content'])

        # Commit the file.
        repo.index.add([mainfile])
        repo.index.write()
        repo.index.commit(request.form['message'])

        # View the paste.
        return redirect(url_for('view', rid=rid))

@route_fetch_repo
@require_repo_owner
def delete(rid, repo):
    if request.method == 'GET':
        mainfile = get_repo_files(repo)[0]
        directory = repo.working_dir
        title = read_file(os.path.join(directory, 'title'))
        return render_template('delete.html', title=title, rid=rid, repo_owner=we_repo_owner(repo))
    else:
        # Rename the directory.
        directory = repo.working_dir
        os.rename(directory, directory.rstrip('/\\') + '.deleted')

        # Go to the main page.
        return redirect(url_for('new'))
