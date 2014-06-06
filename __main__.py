#!/usr/bin/python

import os
import functools
import settings
from constants import LANGUAGES
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from git import Repo, NoSuchPathError

app = Flask(__name__)
settings.apply(app)
Bootstrap(app)

def get_repo(f):
    """
    Helper function that will automatically grab the rid parameter and load the
    repo associated with it. If this fails, it will throw an FlaskError.
    """
    @functools.wraps(f)
    def wrapper(rid, *args, **kwargs):
        try:
            repo = Repo(os.path.join(settings.repodir, rid))
        except NoSuchPathError:
            return render_template('error.html', message='That paste does not exist')
        return f(rid=rid, repo=repo, *args, **kwargs)
    return wrapper

def read_file(fn):
    """
    Read the entire file into a string.
    """
    with open(fn, 'r') as f:
        return f.read()

@app.route('/', methods=('GET', 'POST'))
@app.route('/new', methods=('GET', 'POST'))
def new():
    if request.method == 'GET':
        return render_template('edit.html', title='New Paste', message='Initial version', new=True, languages=LANGUAGES)
    else:
        # Check that all required fields are present.
        if not set(('title', 'message', 'language', 'content')).issubset(set(request.form.keys())):
            flash('Please fill in all fields', 'warning')
            return render_template('edit.html', new=True, languages=LANGUAGES, **request.form)

        # Get the next free ID.
        rid = max([int(f) for f in os.listdir(settings.repodir)] + [0]) + 1

        # Create a new repo.
        directory = os.path.join(settings.repodir, str(rid))
        repo = Repo.init(directory)
        
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

@app.route('/list')
def list():
    return render_template('list.html')

@app.route('/<rid>')
@app.route('/<rid>/<rev>')
@get_repo
def view(rid, repo, rev='HEAD'):
    return render_template('view.html', rid=rid)

@app.route('/<rid>/edit', methods=('GET', 'POST'))
@get_repo
def edit(rid, repo):
    files = [entry[0] for entry in repo.index.entries.keys()]
    files.remove('title')
    directory = repo.working_dir
    mainfile = files[0]
    if request.method == 'GET':
        title = read_file(os.path.join(directory, 'title'))
        content = read_file(os.path.join(directory, mainfile))
        return render_template('edit.html', title=title, content=content, rid=rid)
    else:
        # Check that all required fields are present.
        if not set(('message', 'content')).issubset(set(request.form.keys())):
            flash('Please fill in all fields', 'warning')
            return render_template('edit.html', rid=rid, **request.form)

        # Write the paste to a file.
        with open(os.path.join(directory, mainfile), 'w') as f:
            f.write(request.form['content'])

        # Commit the file.
        repo.index.add([mainfile])
        repo.index.write()
        repo.index.commit(request.form['message'])

        # View the paste.
        return redirect(url_for('view', rid=rid))

@app.route('/<rid>/delete', methods=('GET', 'POST'))
@get_repo
def delete(rid, repo):
    return render_template('delete.html', rid=rid)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
