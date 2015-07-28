from os import listdir, getcwd, makedirs, remove
import string
import random
from os.path import isdir, isfile, exists
from os.path import join as join_path, abspath, realpath
from os.path import split as split_path
from os.path import getsize, getmtime, relpath
from os.path import sep
from shutil import rmtree
from cork import Cork
from bottle import abort, response, static_file

DEBUG = True
PATH_ERROR = "The path is not available or doesn't exist"
aaa = Cork('cork_conf')
root_dir = join_path(getcwd(), 'files')
dir_sep = "#" + sep
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
type_to_path = {
    'files': permitted_files_path,
    'config': permitted_config_path,
    'shares': permitted_shares_path}

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
    """prepares a list of files and folders ready for the API.
    if a user is connected, we can see the sharing IDs associated to each.
    path: absolute path to list
    details: see files and folders informations
    """
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
                    for x in get_uid_from_path(ls_path)]
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


def get_config(rel_path, key, subdir='config'):
    """Get configuration from folder/path
    """
    Ukey = key + "K"
    Upath = prep_upath(rel_path)
    print(Upath)
    config_path = protect_path(Upath, subdir)
    path = config_path
    print(path)
    if not exists(path) or not isdir(path):
        raise IOError("The key doesn't exist")
    path = join_path(path, Ukey)
    if not exists(path):
        return defaults[key]
    else:
        with open(path, 'r') as f:
            value = f.read()
        return value


def get_uid_from_path(path):
    """
    Get a list of sharing IDs associated to a path.
    path: path relative to a users folder
    """
    # get path relative to the permitted path where we upload files
    rel_path = relpath(path, permitted_files_path())
    # get a path in the form of <path>#/<path#>...
    Upath = prep_upath(rel_path)
    # get the protected path in the configuration folder
    config_path = protect_path(Upath, 'config')
    print(("config path is", config_path))
    if isdir(config_path):
        shares_names = prep_ls(config_path, False)['files']
        sharing_uids = [x[:-1] for x in shares_names]
        return sharing_uids
    return []


def get_path_from_uid(user, uid):
    # config/user/shares/uid
    return get_config(uid, 'path', '{}/shares'.format(user))


def delete_path(real_path):
    if exists(real_path):
        if isfile(real_path):
            if DEBUG:
                return {real_path: 'deleted'}
            else:
                remove(real_path)
        elif isdir(real_path):
            if DEBUG:
                return {real_path: 'deleted'}
            else:
                rmtree(real_path)


def check_config_path(rel_path, subdir='config'):
    """prepares config folder and check everything is fine
    rel_path: path relative to the 'subdir'
    """
    Upath = prep_upath(rel_path)
    # print("going to try to create {}".format(Upath))
    config_path = protect_path(Upath, subdir)
    print(config_path)
    # print("in {}".format(config_path))
    try:
        return create_path(config_path)
    except IOError:
        raise


def create_path(path):
    """prepares config folder and check everything is fine
    returns True if created False if not. Raises an exception if it's a file
    """
    if exists(path):
        if not isdir(path):
            raise IOError("Configuration path is not accessible")
        return False
    else:
        makedirs(path)
        return True


def create_random_folder():
    count = 0
    ruid = random_generator()
    while not check_config_path(ruid, 'shares') and count < 10:
        ruid = random_generator()
        count += 1
    # return ruid, create
    return ruid, ruid


def prep_upath(rel_path):
    # print("&" * 80)
    # unique path to avoid key vs path collision
    if rel_path.startswith(sep):
        rel_path = rel_path[1:]
    if not rel_path.endswith(sep):
        rel_path = rel_path + sep
    split_path = rel_path.split(sep)
    # print(split_path)
    # relative unique path
    Upath = dir_sep.join(split_path)
    # print(Upath)
    # print("&" * 80)
    return Upath


def configure(rel_path, key, value=None, subdir='config'):
    """Configure things using folders and files
    value == None: keep default or don't modify the file
    path: /a/b/c/config/some#/path#/
    key: key + "K"
    """
    # absolute config path
    key = key + "K"
    Upath = prep_upath(rel_path)
    config_path = protect_path(Upath, subdir)
    # print("*" * 80)
    # print("got {} {} {} {}".format(rel_path, key, value, subdir))
    # print(config_path)
    create_path(config_path)
    if value is None:
        return config_path
    path = join_path(config_path, key)
    # print(path)
    # print("*" * 80)
    with open(path, 'w') as f:
        f.write(value)


def get_files(path):
    """Check if a path is shared and return the list of aliases"""
    files = list_dir(path)
    return files['files']


def protect_path(path, path_type='files'):
    """Get a path based on permitted paths"""
    f = type_to_path.get(path_type)
    if f is not None:
        permitted = f()
    elif path_type.endswith('shares'):
        permitted = join_path(root_dir, path_type)
    try:
        real_path = get_real_path(permitted, path)
        return real_path
    except IOError:
        abort(403)


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
