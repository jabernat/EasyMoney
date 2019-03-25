#TODO:
        #Events:
                #MARKET_DATASOURCE_CAN_CONFIRM_UPDATED,
                #MARKET_DATASOURCE_CONFIRMATION_UPDATED,
                #MARKET_DATASOURCE_MODE_CHANGED,
                #MARKET_DATASOURCE_STOCK_SYMBOL_ADD_LIVE_ERROR,
                #MARKET_DATASOURCE_STOCK_SYMBOL_REMOVED

class AlphaVantageApiKeyMissingError(RuntimeError):
        """
        An exception raised when attempting to access Alpha Vantage without
        specifying an API key.
        """
        pass

class DatasourceConfirmedError (RuntimeError):
    """
    An exception raised when the datasource has already been confirmed and a
    configuration attempt has been made.
    """
    pass

class DatasourcesMissingError (RuntimeError):
    """
    An exception raised when using this MarketDatasource ’s .confirm() method if
    no stock symbols have been added yet.
    """
    pass

class WrongModeError (RuntimeError):
    """
    An exception raised when the module attempts to add stock symbols with an
    invalid method for the current mode.
    """
    pass

class MarketDatasource:
    """
    Depending on the source, this component has the ability to collate data and
    pass it to the SimModel. If the source is live, an API key is used to
    connect to Alpha Vantage to retrieve the newest stock information. If the
    source is offline, data is gathered from historical JSON files. Any
    pertinent datasource changes are broadcasted to the Window View module.
    """

    def _init__ (self) -> None:
        """
        The constructor for MarketDatasource , which is initialized with no
        starting stock symbols.
        """
        pass
    def add_stock_symbol_archive (self,
                                    json_filename : str
                                    ) -> None:
        """
        This method loads a JSON file with a name json_filename for an
        individual stock symbol. If the file is for a stock symbol which has
        already been added, the data for the previously added symbol is
        replaced. The method may raise the following exceptions for failed
        preconditions: MarketDatasource.WrongModeError if this datasource
        isn’t in archive mode, and MarketDatasource.DatasourceConfirmedError if
        the datasource has already been confirmed.
        If this call succeeds at first, it later fires one of two events:
        MARKET_DATASOURCE_STOCK_SYMBOL_ADDED if successful, or
        MARKET_DATASOURCE_STOCK_SYMBOL_ADD_ARCHIVE_ERROR if an error occurs.
        """
        pass
    def add_stock_symbol_live (self,
                                stock_symbol : str
                                ) -> None:
        """
        This method queries Alpha Vantage to confirm it has data for
        stock_symbol . An example of a valid stock symbol is “ NYSE:MSFT ”,
        representing Microsoft stock on the New York Stock Exchange.
        The method may raise the following exceptions for failed preconditions:
        MarketDatasource.AlphaVantageApiKeyMissingError if an API key has not
        yet been set, MarketDatasource.WrongModeError if this datasource is not
        in live mode, and MarketDatasource.DatasourceConfirmedError if this data
        source is already confirmed. If this call succeeds at first, it later
        fires one of two main events: MARKET_DATASOURCE_STOCK_SYMBOL_ADDED
        if successfully added, or MARKET_DATASOURCE_STOCK_SYMBOL_ADD_LIVE_ERROR
        if stock_symbol could not be found on Alpha Vantage.
        """
        pass
    def can_confirm (self) -> bool:
        """
        The behavior of this method depends on what mode is in use. If in
        archive mode, the method returns True if there is at least one stock
        symbol added and there are no pending symbol additions from
        MarketDatasource.add_stock_symbol_archive(…) . If in live mode, the
        method returns True if there is at least one stock symbol has been
        added, there are no
        pending symbol additions from MarketDatasource.add_stock_symbol_live(…),
        and an API key has been set. Otherwise the method returns False .
        """
        pass

    def confirm (self) -> None:
        """
        This method disables the ability to add or remove stock symbols and
        enables this MarketDatasource to use its .get_next_prices() function.
        This method may only be called if this MarketDatasource ’s datasource is
        prepared to be read. If no stock symbols have been added, this method
        will raise a MarketDatasource.DatasourcesMissingError exception. If
        no API key has been set in “ LIVE ” mode, this method raises a
        MarketDatasource.AlphaVantageApiKeyMissingError exception.
        """
        pass
    
    def get_live_api_key (self) -> typing.Optional[str]:
        """
        This method returns a string containing the currently configured Alpha
        Vantage API key, or None if it has not yet been specified.
        """
        pass
    
    def get_mode (self) -> str:
        """
        This method returns a string that signifies which mode is in use. The
        modes can be either “ LIVE ” or “ ARCHIVE .”
        """
        pass       
    def get_next_prices (self
            ) -> typing.Optional[(datetime.datetime, typing.Dict[str, float])]:

        """
        A blocking call that returns None if this datasource hasn't begun yet or
        if no more prices are left in the datasource. Otherwise, this call halts
        until a new batch of prices has been collected. Getting the next data in
        “ LIVE ” mode in particular may be slow, so query it from a background
        thread.
        """
        pass
    
    def get_stock_symbols (self) -> typing.List[str]:
        """
        This method returns a list of strings for each stock symbol that has
        been added. The list should change after the following two events:
        MARKET_DATASOURCE_STOCK_SYMBOL_ADDED and
        MARKET_DATASOURCE_STOCK_SYMBOL_REMOVED.
        """
        pass
    
    def is_confirmed (self) -> bool:
        """
        This method returns True if this MarketDatasource’s datasource is ready
        to be read. Otherwise the method returns false .
        """
        pass
    
    def remove_stock_symbol (self,
                            stock_symbol : str
                            ) -> None:
        """    
        This method is used to remove a stock symbol whose name matches the
        passed string. If this method is called after the datasource has already
        been confirmed, this method will throw a
        MarketDatasource.DatasourceConfirmedError exception.
        """
        pass
    
    def set_live_api_key (self,
                            api_key : str
                            ) -> None:
        """
        This method sets the API key for Alpha Vantage access. If this method is
        called after the datasource has already been confirmed, this method will
        throw a MarketDatasource.DatasourceConfirmedError exception.
        """
        pass
        
    def set_mode (self,
                    mode : str
                    ) -> None:
        """
        Given a string, this method sets which datasource will be used. The new
        mode must be either of the two strings “LIVE” or “ARCHIVE.” If the
        datasource has not been confirmed and the mode is changed, the list of
        added stock symbols is cleared. If the datasource has been confirmed and
        this method is called, a MarketDatasource.DatasourceConfirmedError
        exception is thrown.
        """
        pass
    
    def unconfirm (self) -> None:
        """
        This method enables the ability to add or remove stock symbols and
        prevents this MarketDatasource’s ability to use its .get_next_prices()
        function.
        """
        pass
