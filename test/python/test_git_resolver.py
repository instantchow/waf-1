import os
import pytest
import mock

from wurf.git_resolver import GitResolver


def test_git_resolver(test_directory):

    ctx = mock.Mock()
    git = mock.Mock()
    cwd = test_directory.path()

    # GitResolver checks that the directory is created during git.clone,
    # so we create it within the test_directory as a side effect
    def fake_git_clone(repository, directory, cwd):
        test_directory.mkdir(directory)

    git.clone = mock.Mock(side_effect=fake_git_clone)

    name = 'links'
    repo_url = 'https://gitlab.com/steinwurf/links.git'

    resolver = GitResolver(git=git, ctx=ctx, name=name,
        bundle_path=cwd, source=repo_url)

    path = resolver.resolve()

    # The destination path is determined in the resolve function,
    # we just get the folder name manually
    repo_name = os.path.basename(os.path.normpath(path))

    git.clone.assert_called_once_with(
        repository=repo_url, directory=repo_name, cwd=cwd)

    git.pull_submodules.assert_called_once_with(cwd=path)

    # Reset the git mock
    git.reset_mock()

    # The destination folder is already created, so the next resolve
    # should just run git pull
    path2 = resolver.resolve()

    assert path2 == path

    assert git.clone.called == False
    git.pull.assert_called_once_with(cwd=path)
    git.pull_submodules.assert_called_once_with(cwd=path)
