from bottle import run, request, abort, get, post
from os import listdir, getcwd
from os.path import join as join_path, abspath, realpath, split as split_path
from os.path import isdir, isfile, exists

root_dir = getcwd()
files_path = 'files'
permitted_path = join_path(root_dir, files_path)


def get_real_path(restrict=permitted_path, path=None):
    """Normalize a path and returns one relative to the permitted
    `files_path`

    Asking for 'tmp' should give us a path in our permitted folder
    >>> get_real_path('/my/folder', 'tmp')
    '/my/folder/tmp'

    As should asking for 'blah/../tmp' should work
    >>> get_real_path('/my/folder', 'blah/../tmp')
    '/my/folder/tmp'

    Asking for '/tmp' should fail
    >>> get_real_path('/my/folder', '/tmp')
    Traceback (most recent call last):
    ...
    IOError: /tmp doesn't exist

    Same if we ask for '../../../../tmp'
    >>> get_real_path('/my/folder', '/tmp')
    Traceback (most recent call last):
    ...
    IOError: /tmp doesn't exist
    """
    # print((restrict, path))
    path = join_path(restrict, path)
    path = abspath(path)
    path = realpath(path)
    if path.startswith(restrict):
        return path
    else:
        raise IOError("{} doesn't exist".format(path))


def list_dir(path):
    """Return folder content or filename
    """
    ls = {'dirs': [], 'files': []}
    if isdir(path) and exists(path):
        _ls = listdir(path)
        for p in _ls:
            ls_path = join_path(path, p)
            if isdir(ls_path):
                ls['dirs'].append(p)
            elif isfile(ls_path):
                ls['files'].append(p)
    elif isfile(path):
        return path
    return ls


@get('/files/<user>')
@get('/files/<user>/<path:path>')
def list_path(user, path='.'):
    """Return a list of files in a path if permitted
    """
    permitted = join_path(permitted_path, user)
    try:
        real_path = get_real_path(permitted, path)
    except IOError:
        abort(403)
    if user == request.params.get('user'):
        try:
            return list_dir(real_path)
        except OSError:
            abort(404)


@post('/files/<user>')
@post('/files/<user><path:path>')
def create(user, path='.'):
    """Create a folder or a file"""
    permitted = join_path(permitted_path, user)
    try:
        real_path = get_real_path(permitted, path)
    except IOError:
        abort(403)
    file_type = request.params.get('type')
    if file_type == "file":
        _path, _file = split_path(real_path)
        if request.files:
            print("we have a file")
        else:
            print("create empty file")
    elif file_type == 'dir':
        print("create a directory")

if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True, reloader=True)
