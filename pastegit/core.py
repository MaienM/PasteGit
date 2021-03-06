import os
import settings
import math

from flask import render_template, request, redirect, url_for, flash, session, g

from constants import LANGUAGES
from pasterepo import PasteRepo

def index():
    return render_template('index.html')

def new():
    if not g.user.can_create():
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
        cw.set('user', 'name', g.user.name)
        cw.set('user', 'email', g.user.email)
        cw.write()

        # Commit.
        repo.update(request.form['message'], request.form['title'], request.form['content'])

        # Message.
        flash('Paste created', 'success')
        
        # View the paste.
        return redirect(url_for('view', rid=repo.id))

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

@PasteRepo.fetch()
def view(repo):
    content = repo.get_content()
    if 'renderer' in repo.language:
        content = repo.language['renderer'](content)
    
    return render_template('view/{}.html'.format(repo.language['view']), content=content, repo=repo)

@PasteRepo.fetch('edit')
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
        return redirect(url_for('view', rid=repo.id))

@PasteRepo.fetch('delete')
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

@PasteRepo.fetch()
def history(repo):
    return render_template('history.html', repo=repo)

@PasteRepo.fetch()
def releases(repo):
    if request.method == 'GET':
        return render_template('releases.html', repo=repo)
    else:
        # Check permission.
        if not g.user.can_edit(repo):
            return 'You are not allowed to edit this paste', 403

        newtag = request.form['value']

        # Check whether the tag is free.
        for tag in repo.tags:
            if tag.name == newtag and tag.commit != repo.rev:
                return 'That tag is already in use', 409

        # If a tag is given, set it.
        if newtag:
            repo.create_tag(newtag, ref=repo.rev.hexsha)
            if repo.revtag:
                repo.delete_tag(repo.revtag.name)
            return 'Tag set'
        else:
            if repo.revtag:
                repo.delete_tag(repo.revtag.name)
            return 'Tag removed'
