import os.path
import functools

from flask import render_template, session
from git import Repo, NoSuchPathError

from constants import LANGUAGES
import settings

def route_fetch_repo(f):
    """
    Wrapper for routes that will automatically grab the rid parameter and load
    the repo associated with it. If this fails, it will render the error template.
    """
    @functools.wraps(f)
    def wrapper(rid, *args, **kwargs):
        try:
            repo = Repo(os.path.join(settings.REPODIR, rid))
        except NoSuchPathError:
            return render_template('error.html', error='That paste does not exist')
        return f(rid=rid, repo=repo, *args, **kwargs)
    return wrapper

def we_repo_owner(repo):
    """
    Determines whether the current user is the owner of the given repo.
    """
    try:
        repo_email = repo.config_reader('repository').get('user', 'email')
        assert session['user']['email'] == repo_email
        return True
    except:
        return False

def require_repo_owner(f):
    """
    Require the current user to be the owner of the repo. If this is not the
    case, the error template will be rendered.
    """
    @functools.wraps(f)
    def wrapper(repo, *args, **kwargs):
        if we_repo_owner(repo):
            return f(repo=repo, *args, **kwargs)
        else:
            return render_template('error.html', error='You are not the owner of this paste')
    return wrapper

def get_repo_files(repo):
    """
    Get the files that belong to a repo.

    Static entries (that are in each repo) such as 'title' are stripped.
    """
    files = [entry[0] for entry in repo.index.entries.keys()]
    files.remove('title')
    return files

def read_file(fn):
    """
    Read the entire file into a string.
    """
    with open(fn, 'r') as f:
        return f.read()

def detect_language(fn):
    """
    Detect the language of a file by it's extension.
    """
    ext = '.' + fn.rsplit('.')[-1]
    for lang in LANGUAGES.values():
        if ext in lang['extensions']:
            return lang
    return None
