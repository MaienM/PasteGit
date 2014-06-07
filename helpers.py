import os.path
import functools

from flask import render_template
from git import Repo, NoSuchPathError

from constants import LANGUAGES
import settings

def route_auto_repo(f):
    """
    Wrapper for routes that will automatically grab the rid parameter and load
    the repo associated with it. If this fails, it will render the error template.
    """
    @functools.wraps(f)
    def wrapper(rid, *args, **kwargs):
        try:
            repo = Repo(os.path.join(settings.repodir, rid))
        except NoSuchPathError:
            return render_template('error.html', message='That paste does not exist')
        return f(rid=rid, repo=repo, *args, **kwargs)
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
    Detect the language of a file by it's extention.
    """
    ext = '.' + fn.rsplit('.')[-1]
    for lang in LANGUAGES.values():
        if ext in lang['extentions']:
            return lang
    return None
