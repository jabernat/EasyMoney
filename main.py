#!/usr/bin/env python3
"""Entry point for the EasyMoney application."""


__copyright__ = 'Copyright © 2019, Erik Anderson, James Abernathy, and Tyler Gerritsen'
__license__ = 'MIT'


from model.sim_model import SimModel
from controller.sim_controller import SimController
from view.window_view import WindowView




def main() -> None:
    """Program entry point that opens the application window."""
    WindowView(SimController(SimModel())).run()




if __name__ == '__main__':
    main()
