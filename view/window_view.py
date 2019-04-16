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


    def run(self
    ) -> None:
        """
        """
        # WindowView(SimController(SimModel())).run()
        print('Welcome to EasyMoney')

        # TRADER
        names = ['Madoff', 'Belfort', 'Stewart']
        initial_funds: float = 10000.0
        trading_fee: float = .05
        momentum_trader = MomentumTrader()
        algorithm: str = momentum_trader.get_algorithm_name()
        algorithm_settings: dict = momentum_trader.get_algorithm_settings_defaults()
        print('Adding traders')
        try:
            for name in names:
                self._sim_controller.add_trader(name,
                                                initial_funds,
                                                trading_fee,
                                                algorithm,
                                                algorithm_settings)
        except Exception as e:
            print(e)
        print('Traders Madoff, Belfort, Stewart successfully added.\n')

        # DATASOURCE
        file_names = ['AAPL.json', 'MSFT.json', 'AMD.json', 'JCOM.json']
        print('Adding datasources.')
        for filename in file_names:
            try:
                self._sim_controller.get_datasource().add_stock_symbol(filename)
            except Exception as e:
                print(e)
        try:
            if self._sim_controller.get_datasource().can_confirm():
                self._sim_controller.get_datasource().confirm()
        except Exception as e:
            print(e)
        print('Datasources successfully added.\n')

        # SIMULATION
        print('Starting simulation.')
        try:
            self._sim_controller.get_updater().play()
        except Exception as e:
            print(e)
        print('Simulation complete.\n')

        # STATISTICS
        print('Statistics display:')
        trader_list = self._sim_controller.get_model().get_traders()
        for trader in trader_list:
            try:
                print('Trader: ' + trader.get_name())
                print(trader.get_account().get_statistics_overall())
                print()
            except Exception as e:
                print(e)

        print('\nThank you for using EasyMoney.')

# Imported last to avoid circular dependencies
from controller.sim_controller import SimController
from model.algorithms.momentum_trader import MomentumTrader

