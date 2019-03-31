"""Defines `WindowView` and supporting classes."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


import typing

# Local package imports at end of file to resolve circular dependencies




class WindowView(object):
    """
    """


    _sim_controller: 'SimController'
    """"""


    def __init__(self,
        sim_controller: 'SimController'
    ) -> None:
        """
        """
        self._sim_controller = sim_controller


    def get_controller(self
    ) -> 'SimController':
        """
        """
        return self._sim_controller


    def run() -> None:
        """
        """
        pass




# Imported last to avoid circular dependencies
from controller.sim_controller import SimController
