import os
import pytest
from . import testdirectory

@pytest.fixture
def test_directory(tmpdir):
    """ Creates the PyTest fixture to make it usable withing the unit tests.
    See the TestDirectory class in testdirectory.py for more information.
    """
    return testdirectory.TestDirectory(tmpdir)


def test_fixture(test_directory):
    """ Unit test for the test_directory fixture"""
    assert os.path.exists(test_directory.path())

    subdir = test_directory.mkdir('sub')
    assert os.path.exists(subdir.path())

    subdir.write_file('ok.txt', 'hello_world')

    ok_path = os.path.join(subdir.path(), 'ok.txt')

    assert os.path.isfile(ok_path)
