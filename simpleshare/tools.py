from os import listdir, getcwd, makedirs, remove
import string
import random
from os.path import isdir, isfile, exists
from os.path import join as join_path, abspath, realpath
from os.path import split as split_path
from os.path import getsize, getmtime, relpath
from shutil import rmtree
from cork import Cork
from bottle import abort, response, static_file

DEBUG = True
PATH_ERROR = "The path is not available or doesn't exist"
aaa = Cork('cork_conf')
root_dir = join_path(getcwd(), 'files')
files_path = 'files'
config_path = 'config'
uidshares_path = 'shares'
permitted_path = lambda user, postfix: join_path(root_dir, user, postfix)
permitted_files_path = lambda: permitted_path(
    aaa.current_user.username, files_path)
permitted_config_path = lambda: permitted_path(
    aaa.current_user.username, config_path)
permitted_shares_path = lambda: permitted_path(
    aaa.current_user.username, uidshares_path)

defaults = {
    'public': True,
    'users': None,
    'expires': False
    }

sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB']


def nice_size(size):
    mul = len(str(size))/3
    size = float(size) / float(1 << (10 * mul))
    return "{:.2f} {}".format(size, sizes[mul])


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


def prep_ls(path, details=True):
    ls = {'dirs': [], 'files': []}
    _ls = listdir(path)
    if aaa.user_is_anonymous:
        user = None
    else:
        user = aaa.current_user
    for p in _ls:
        ls_path = join_path(path, p)
        if details:
            f = {'name': p,
                 'size': nice_size(getsize(ls_path)),
                 'mtime': getmtime(ls_path),
                 }
            if user:
                shares = [
                    (user.username, x)
                    for x in get_uid_from_path(ls_path)['files']]
                # print('share list for {}: {}'.format(ls_path, shares))
                f['shares'] = shares
        else:
            f = p
        if isdir(ls_path):
            ls['dirs'].append(f)
        elif isfile(ls_path):
            ls['files'].append(f)
    return ls


def list_dir(path):
    """Return folder content or filename
    """
    try:
        if isdir(path) and exists(path):
            ls = prep_ls(path)
            return ls
        elif isfile(path):
            if DEBUG:
                root, filename = split_path(path)
                return static_file(filename, root=root, download=True)
            else:
                response.headers['X-Accel-Redirect'] = path
                return ''
    except OSError:
        abort(404)


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


def get_uid_from_path(path):
    path_config_path = permitted_config_path()
    rel_share_path = relpath(path, permitted_files_path())
    path_config_path = join_path(path_config_path, rel_share_path)
    # print("in get_uid {}".format(path))
    # print("in get_uid share config path is {}".format(share_config_path))
    if isdir(path_config_path):
        shares_names = prep_ls(path_config_path, False)
        # print("in get_uid isdir {}".format(shares_names))
        return shares_names
    return {'files': []}


def get_path_from_uid(user, uid):
    config = permitted_path(user,
                            join_path(uidshares_path, uid))
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
    ruid = random_generator()
    create = join_path(path, ruid)
    while isdir(create) and exists(create) and count < 10:
        ruid = random_generator()
        create = join_path(path, ruid)
        count += 1
    check_config_path(create)
    return ruid, create


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


def protect_path(path, path_type='files'):
    if path_type == 'files':
        permitted = permitted_files_path()
    elif path_type == 'config':
        permitted = permitted_config_path()
    elif path_type == 'shares':
        permitted = permitted_shares_path()
    try:
        real_path = get_real_path(permitted, path)
    except IOError:
        abort(403)
    return real_path


def relist_parent_folder(path):
    try:
        # after deleting we want to re-list what the current folder hosts
        # append /..
        # follow symlink ???
        # get absolutepath
        permitted = abspath(realpath(join_path(path, '..')))
        assert path.startswith(permitted)
    except:
        abort(403, PATH_ERROR)
    ls = list_dir(permitted)
    if DEBUG:
        ls['dirs'].append({'name': 'edited something'})
        ls['files'].append({'name': 'edited {}'.format(path)})
    return ls


def validate_path(path):
    """Check if a path exists in config
    which means the path has been shared with an identicall UID"""
    abs_config_path = protect_path(path, 'config')
    if exists(abs_config_path) and isfile(abs_config_path):
        return False
    return True
