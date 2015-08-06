from os.path import isdir, exists
from os.path import join as join_path
from os.path import sep, abspath, realpath
from os import makedirs

DEBUG = True
dir_sep = "#" + sep
try:
    from settings import defaults
except:
    defaults = {}


def get_real_path(jail, path=None):
    """Normalize a path and returns one relative to the permitted
    `files_path`
    """
    path = join_path(jail, path)
    path = abspath(path)
    # follow symlinks ????
    path = realpath(path)
    if path.startswith(jail):
        return path
    else:
        raise IOError("{} doesn't exist".format(path))


def get_config(root_dir, hash_path, key):
    """Get configuration from folder/path
    """
    Ukey = key + "K"
    Upath = prep_upath(hash_path)
    full_path = get_real_path(root_dir, Upath)
    if not exists(full_path) or not isdir(full_path):
        raise IOError("The key doesn't exist")
    path = join_path(full_path, Ukey)
    if not exists(path):
        return defaults.get(key)
    else:
        with open(path, 'r') as f:
            value = f.read()
        return value


def check_config_path(root_dir, hash_path):
    """prepares config folder and check everything is fine
    rel_path: path relative to the 'subdir'
    """
    Upath = prep_upath(hash_path)
    full_path = get_real_path(root_dir, Upath)
    print(full_path)
    try:
        return create_path(full_path)
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


def prep_upath(rel_path):
    # print("&" * 80)
    # unique path to avoid key vs path collision
    if rel_path is None:
        return ''
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


def configure(root_path, hash_path, key, value=None):
    """Configure things using folders and files
    value == None: keep default or don't modify the file
    path: /a/b/c/config/some#/path#/
    key: key + "K"
    """
    # absolute config path
    key = key + "K"
    Upath = prep_upath(hash_path)
    full_path = get_real_path(root_path, Upath)
    create_path(full_path)
    if value is None:
        return full_path
    path = join_path(full_path, key)
    print(path)
    with open(path, 'w') as f:
        f.write(value)



