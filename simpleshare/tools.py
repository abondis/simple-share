from os import listdir, getcwd, makedirs, remove
import string
import random
from os.path import isdir, isfile, exists
from os.path import join as join_path, abspath, realpath
from shutil import rmtree
from cork import Cork
from bottle import abort

aaa = Cork('cork_conf')
root_dir = join_path(getcwd(), 'files')
files_path = 'files'
config_path = 'config'
permitted_path = lambda user, postfix: join_path(root_dir, user, postfix)
permitted_files_path = lambda: permitted_path(
    aaa.current_user.username, files_path)
permitted_config_path = lambda: permitted_path(
    aaa.current_user.username, config_path)


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
    path = join_path(restrict, path)
    path = abspath(path)
    # follow symlinks ????
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


def delete_path(real_path):
    if exists(real_path):
        if isfile(real_path):
            if DEBUG:
                print("deleting file {}".format(real_path))
            else:
                remove(real_path)
        elif isdir(real_path):
            if DEBUG:
                print("deleting folder {}".format(real_path))
            else:
                rmtree(real_path)


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


def protect_path(path):
    current_user = aaa.current_user.username
    permitted = permitted_path(current_user, files_path)
    try:
        real_path = get_real_path(permitted, path)
    except IOError:
        abort(403)
    return real_path
