import keyval as t
from os import makedirs, path
from shutil import rmtree


def prep_folder(conf=False):
    """prepare a temporary folder
    conf: is it a configuration folder ? else it is just a normal folder
    """
    try:
        rmtree('/tmp/test')
    except:
        pass
    if conf:
        makedirs('/tmp/test/usertest/config/testhash#/XYZ22#')
        makedirs('/tmp/test/usertest/shares/XYZ22#')
        with open('/tmp/test/usertest/config/testhash#/XYZ22K', 'w') as f:
            f.write('a')
        with open(
                '/tmp/test/usertest/shares/XYZ22#/pathK',
                'w') as f:
            f.write('/test/path')
        return
    makedirs('/tmp/test/folder')
    with open('/tmp/test/file', 'w') as f:
        f.write('a')


def del_folder(conf=False):
    rmtree('/tmp/test')


def test_create_path():
    """Create a folder if it doesn't exist"""
    prep_folder(True)
    r = t.create_path('/tmp/test/blahblah')
    assert r is True
    try:
        t.create_path('/tmp/test/usertest/config/testhash#/XYZ22K')
        assert False, "Creating a path on a file should fail"
    except Exception as e:
        assert e.message == "Configuration path is not accessible"
    del_folder(True)


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


def test_get_config():
    """Query a key in a specific path"""
    prep_folder(True)
    val = t.get_config('/tmp/test/usertest/config', 'testhash', 'XYZ22')
    assert val == 'a'
    val = t.get_config('/tmp/test/usertest/config/testhash#', None, 'XYZ22')
    assert val == 'a'
    del_folder(True)


def test_check_config_path():
    """prepares config folder and check everything is fine
    returns True if created False if not. Raises an exception if it's a file
    """
    prep_folder(True)
    val = t.check_config_path('/tmp/test/usertest/config', 'testhash')
    assert val is False
    val = t.check_config_path('/tmp/test/usertest/config', 'blah')
    assert val is True
    del_folder(True)


def test_prep_upath():
    """I want to get a Unique path for a specific path in the KV store"""
    r = t.prep_upath('relative/path')
    assert r == 'relative#/path#/'
    r = t.prep_upath('/relative/path')
    assert r == 'relative#/path#/'
    r = t.prep_upath('relative/path/')
    assert r == 'relative#/path#/'


def test_configure():
    """Configure a Path/Key with a value"""
    t.configure('/tmp/test/usertest/config',
                'some/path', 'somekey', 'somevalue')
    assert path.isdir('/tmp/test/usertest/config/some#')
    assert path.isdir('/tmp/test/usertest/config/some#/path#')
    assert path.isfile('/tmp/test/usertest/config/some#/path#/somekeyK')
    assert open(
        '/tmp/test/usertest/config/some#/path#/somekeyK',
        'r').read() == 'somevalue'
