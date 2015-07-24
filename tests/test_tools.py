from simpleshare import tools as t
from os import makedirs, path
from shutil import rmtree
from mock import patch


def prep_folder(conf=False):
    """prepare a temporary folder
    conf: is it a configuration folder ? else it is just a normal folder
    """
    try:
        rmtree('/tmp/test')
    except:
        pass
    if conf:
        makedirs('/tmp/test/usertest/config/testhash#')
        with open('/tmp/test/usertest/config/testhash#/XYZ22K', 'w') as f:
            f.write('a')
        return
    makedirs('/tmp/test/folder')
    with open('/tmp/test/file', 'w') as f:
        f.write('a')


def del_folder(conf=False):
    rmtree('/tmp/test')


def test_nice_size():
    """Depending on the size in bytes of a file, I want it's size in B,
    KiB, MiB etc"""
    assert t.nice_size(1) == '1.00 B'
    assert t.nice_size(104) == '0.10 KiB'
    assert t.nice_size(1024) == '1.00 KiB'
    assert t.nice_size(104000) == '0.10 MiB'
    assert t.nice_size(1048576) == '1.00 MiB'


def test_random_generator():
    """I'd like at least 1000's of generated strings to be different"""
    results = [t.random_generator() for x in xrange(1, 10000)]
    results_set = set(results)
    assert len(results) > 9990
    assert len(results_set) > 9990


def test_get_real_path():
    """I want to get an absolute, cleaned path that is really inside the
    'permitted' path"""

    # Asking for 'tmp' should give us a path in our permitted folder
    r = t.get_real_path('/my/folder', 'tmp')
    assert r == '/my/folder/tmp'

    # As should asking for 'blah/../tmp' should work
    r = t.get_real_path('/my/folder', 'blah/../tmp')
    assert r == '/my/folder/tmp'

    # Asking for '/tmp' should fail
    try:
        t.get_real_path('/my/folder', '/tmp')
        assert False
    except IOError as e:
        assert e.message == "/tmp doesn't exist"

    # Same if we ask for '../../../../tmp'
    try:
        t.get_real_path('/my/folder', '../../../tmp')
        assert False
    except IOError as e:
        assert e.message == "/tmp doesn't exist"


@patch('simpleshare.tools.aaa')
def test_prep_ls(aaa):
    """I want to get a simple list of files and folders separated by type"""
    aaa.user_is_anonymous = True
    prep_folder()
    ls = t.prep_ls('/tmp/test', details=False)
    del_folder()
    assert ls == {'files': ['file'], 'dirs': ['folder']}


@patch('simpleshare.tools.aaa')
def test_prep_ls_details(aaa):
    """I want to get a list of files and folders separated by type
    with details about the folder:
    - name, size, mtime
    """
    aaa.user_is_anonymous = True
    prep_folder()
    ls = t.prep_ls('/tmp/test', details=True)
    del_folder()
    assert {'name', 'size', 'mtime'} == set(ls['dirs'][0].keys())
    assert {'name', 'size', 'mtime'} == set(ls['files'][0].keys())


@patch('simpleshare.tools.aaa')
def test_list_dir_folder(aaa):
    """Get a list of files in a specific folder"""
    aaa.user_is_anonymous = True
    prep_folder()
    ls = t.list_dir('/tmp/test')
    del_folder()
    assert {'name', 'size', 'mtime'} == set(ls['dirs'][0].keys())
    assert {'name', 'size', 'mtime'} == set(ls['files'][0].keys())


@patch('simpleshare.tools.static_file')
def test_list_dir_file(static_file):
    """Listing a 'file' gives us it's content or path when not in debug"""
    prep_folder()
    t.list_dir('/tmp/test/file')
    del_folder()
    assert static_file.called


@patch('simpleshare.tools.aaa')
def test_get_config(aaa):
    """Query a key in a specific path"""
    aaa.current_user.username = 'usertest'
    t.root_dir = '/tmp/test'
    prep_folder(True)
    val = t.get_config('testhash', 'public')
    assert val is True
    del_folder(True)


@patch('simpleshare.tools.aaa')
def test_get_uid_from_path(aaa):
    """Get a list of sharing UID associated to a specific path
    it is called with a path relative to the configuration
    """
    aaa.current_user.username = 'usertest'
    t.root_dir = '/tmp/test'
    prep_folder(True)
    r = t.get_uid_from_path('/tmp/test/usertest/files/testhash')
    assert r == ['XYZ22']


def test_get_path_from_uid():
    """Find the path shared from a specific sharing UID"""
    assert False


def test_delete_path():
    """Delete a file or a folder"""
    assert False


def test_check_config_path():
    """prepares config folder and check everything is fine"""
    assert False


def test_create_path():
    """Create a folder if it doesn't exist"""
    assert False


def test_create_random_folder():
    """Get a sharing UID that doesn't already exist"""
    assert False


def test_prep_upath():
    """I want to get a Unique path for a specific path in the KV store"""
    assert False


def test_configure():
    """Configure a Path/Key with a value"""
    assert False


def test_get_files():
    """Get only the file list from the listing of a path"""
    assert False


@patch('simpleshare.tools.aaa')
@patch('simpleshare.tools.abort')
def test_protect_path(abort, aaa):
    """I want to get a clean safe path inside one of the configured
    authorized paths"""
    aaa.current_user.username = 'usertest'
    t.root_dir = '/tmp/test/files'
    val = t.protect_path('some/rel/path')
    assert val == path.join(t.root_dir, 'usertest', 'files', 'some/rel/path')
    val = t.protect_path('some/rel/path', 'config')
    assert val == path.join(t.root_dir, 'usertest', 'config', 'some/rel/path')
    val = t.protect_path('/some/rel/path', 'config')
    abort.assert_called_with(403)


def test_relist_parent_folder():
    """Get a list of files and folders in the parent of the specified path"""
    assert False


def test_validate_path():
    """Check if a path exists in the config, to avoid creating a folder
    with the same name as the path"""
    # Might not be needed anymore
    assert False
