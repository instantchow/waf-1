#! /usr/bin/env python
# encoding: utf-8

import os

from .error import DependencyError

class PathResolver(object):
    """
    User Path Resolver functionality. Allows the user to specify the path.
    """

    def __init__(self, dependency, path):
        """ Construct an instance.

        :param dependency: A Dependency instance.
        :param path: A path to the dependency
        :param ctx: A Waf Context instance.
        """
        self.dependency = dependency
        self.path = path

    def resolve(self):
        """
        :return: The user specified path.
        """

        self.path = os.path.abspath(os.path.expanduser(self.path))

        if not os.path.isdir(self.path):
            raise DependencyError('Path error: "{}" is not a valid '
                'directory'.format(self.path), dependency=self.dependency)

        return self.path
