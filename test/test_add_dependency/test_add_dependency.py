
def test_add_dependency(test_directory):
    """ Integration testing of adding a dependency."""

    test_directory.copy_file('build/*/waf')
    test_directory.copy_file('test/test_add_dependency/wscript')

    r = test_directory.run('python', 'waf', 'configure', '-v')

    assert r.returncode == 0, str(r)

    r = test_directory.run('python', 'waf', 'build', '-v')

    assert r.returncode == 0, str(r)
