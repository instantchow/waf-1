import pytest
import mock

from wurf.dependency import Dependency

def test_dependency():

    dep = \
    {
        "name": "waf",
        "optional": True,
        "recurse": False,
        "resolver": "git",
        "method": "checkout",
        "checkout": "somebranch",
        "sources": ["gitrepo1.git", "gitrepo2.git"]
    }

    w = Dependency(**dep)

    assert w.name == "waf"
    assert w.optional == True
    assert w.recurse == False
    assert w.resolver == "git"
    assert w.method == "checkout"
    assert w.checkout == "somebranch"
    assert w.sources == ["gitrepo1.git", "gitrepo2.git"]

    # Check there is a sha1 key
    assert "sha1" in w
    assert len(w.sha1) > 0

    # Check that we cannot change the read-only attributes (the ones passed
    # at construction time)
    with pytest.raises(Exception):
        w.name = "waf2"

    w.name2 = "waf2"
    assert w.name2 == "waf2"

    assert w.path is None
    assert ('path' in w) == False

    w.rewrite(attribute='method', value='semver', reason='testing it')
    w.rewrite(attribute='major', value=3, reason='testing it')
    w.rewrite(attribute='checkout', value=None, reason='testing it')

    assert w.method == "semver"
    assert w.major == 3
    assert 'checkout' not in w


def test_dependency_default_values():

    dep = \
    {
        "name": "foo",
        "resolver": "git",
        "method": "checkout",
        "sources": ["gitrepo1.git", "gitrepo2.git"]
    }

    w = Dependency(**dep)

    # Check the explicitly defined attributes
    assert w.name == "foo"
    assert w.resolver == "git"
    assert w.method == "checkout"
    assert w.sources == ["gitrepo1.git", "gitrepo2.git"]

    # Check the default values
    assert w.recurse == True
    assert w.optional == False
    assert w.internal == False

    # Check there is a sha1 key
    assert "sha1" in w
    assert len(w.sha1) > 0
