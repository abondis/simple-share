from bottle import run, request, abort, get, post
from os import listdir, getcwd, makedirs
from os.path import join as join_path, abspath, realpath, split as split_path
from os.path import isdir, isfile, exists, relpath, basename
import string
import random
# from base64 import b64decode

root_dir = join_path(getcwd(), 'files')
files_path = 'files'
config_path = 'config'
permitted_path = lambda user, postfix: join_path(root_dir, user, postfix)


def random_generator(size=4, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


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
    print((path, restrict))
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

defaults = {
    'public': True,
    'users': None,
    'expires': False
    }


def get_config(path, key, subdir=None):
    """Get configuration from folder/path
    """
    if subdir is not None:
        path = join_path(path, subdir)
    path = join_path(path, key)
    if not exists(path):
        return defaults[key]
    else:
        with open(path, 'r') as f:
            value = f.read()
        return value


def get_path_from_uid(user, uid):
    config = permitted_path(user,
                            join_path(config_path, uid))
    if isdir(config):
        return get_config(config, 'path')
    return None


@get('/shared/<user>/<uid>')
@get('/shared/<user>/<uid>/<path:path>')
def list_shared(user, uid, path='.'):
    """Return a list of files in a shared folder"""
    shared_path = get_path_from_uid(user, uid)
    print(shared_path)
    try:
        permitted = join_path(root_dir, shared_path)
        real_path = get_real_path(permitted, path)
        print(real_path)
    except IOError:
        print('error')
        abort(403, "The path is not available or doesn't exist")
    try:
        return list_dir(real_path)
    except OSError:
        abort(404)
    abort(403, {'status': 'ko'})


@get('/files/<user>')
@get('/files/<user>/<path:path>')
def list_path(user, path='.'):
    """Return a list of files in a path if permitted
    """
    current_user = request.params.get('user')
    if current_user is None:
        abort(403)
    permitted = permitted_path(current_user, files_path)
    try:
        real_path = get_real_path(permitted, path)
    except IOError:
        abort(403)
    if user == current_user:
        try:
            return list_dir(real_path)
        except OSError:
            abort(404)
    abort(403, {'status': 'ko'})


@post('/files/<user>')
@post('/files/<user>/<path:path>')
def create(user, path='.'):
    """Create a folder or a file"""
    current_user = request.params.get('user')
    if current_user is None:
        abort(403)
    file_type = request.params.get('type')
    overwrite = request.params.get('overwrite', False)
    permitted = permitted_path(current_user, files_path)
    uploads = request.files

    if user == current_user:
        try:
            real_path = get_real_path(permitted, path)
        except IOError:
            abort(403)
        if file_type == "file":
            _path, _file = split_path(real_path)
            if request.files:
                for f in uploads:
                    uploads.get(f).save(
                        real_path, overwrite=overwrite)
        elif file_type == 'dir':
            if not isdir(real_path) and not exists(real_path):
                print("create a directory")
                makedirs(real_path)
        return {'status': 'ok'}
    abort(403, {'status': 'ko'})


def check_config_path(path):
    """prepares config folder and check everything is fine"""
    if exists(path):
        if not isdir(path):
            raise IOError("Configuration path is not accessible")
    else:
        makedirs(path)


def create_random_folder(path):
    count = 0
    create = join_path(path, random_generator())
    while isdir(create) and exists(create) and count < 10:
        create = join_path(path, random_generator())
        count += 1
    check_config_path(create)
    return create


def configure(path, key, value=None, subdir=None):
    """Configure things using folders and files
    value == None: keep default or don't modify the file
    """
    if value is None:
        return
    if subdir is not None:
        path = join_path(path, subdir)
    check_config_path(path)
    path = join_path(path, key)
    with open(path, 'w') as f:
        f.write(value)


def get_files(path):
    """Check if a path is shared and return the list of aliases"""
    files = list_dir(path)
    return files['files']


@post('/share/<user>')
@post('/share/<user>/<path:path>')
def share(user, path="."):
    """Share a file or a folder"""
    current_user = request.params.get('user')
    reuse = request.params.get('reuse')
    public = request.params.get('public')
    users = request.params.get('users')
    if current_user is None:
        abort(403)
    permitted = permitted_path(current_user, files_path)
    config = permitted_path(current_user, config_path)
    if user == current_user:
        try:
            real_path = get_real_path(permitted, path)
            shared_path = relpath(real_path, permitted)
            config_shared_path = join_path(
                config, shared_path)
            check_config_path(config_shared_path)
        except IOError:
            abort(403)
        if reuse is not None:
            files = get_files(config_shared_path)
            if reuse in files:
                uid_path = join_path(config, reuse)
            else:
                abort(400, "This sharing ID is invalid")
        else:
            uid_path = create_random_folder(config)
        configure(
            config_shared_path,
            basename(uid_path),
            join_path(user, shared_path))
        configure(uid_path, 'path', join_path(user, shared_path))
        configure(uid_path, 'public', public)
        configure(uid_path, 'users', users)
        return {'status': 'ok'}

    abort(403, {'status': 'ko'})

if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True, reloader=True)
