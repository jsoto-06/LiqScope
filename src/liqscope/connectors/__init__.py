"""Módulo de conectores de ingesta para exchanges de criptoactivos."""

from liqscope.connectors.base import ConnectionStatus, DataSource
from liqscope.connectors.binance import BinanceFuturesConnector
from liqscope.connectors.binance_rest import (
    SUPPORTED_SYMBOLS,
    BinanceFuturesRestClient,
    BinanceMarketData,
    BinanceRateLimitError,
    BinanceRestError,
    UnsupportedSymbolError,
)
from liqscope.connectors.bybit import BybitConnector
from liqscope.connectors.multi_exchange import (
    ExchangeMarketQuote,
    MultiExchangeAggregator,
    MultiExchangeSnapshot,
)
from liqscope.connectors.telegram import TelegramClient

__all__ = [
    "SUPPORTED_SYMBOLS",
    "BinanceFuturesConnector",
    "BinanceFuturesRestClient",
    "BinanceMarketData",
    "BinanceRateLimitError",
    "BinanceRestError",
    "BybitConnector",
    "ConnectionStatus",
    "DataSource",
    "ExchangeMarketQuote",
    "MultiExchangeAggregator",
    "MultiExchangeSnapshot",
    "TelegramClient",
    "UnsupportedSymbolError",
]
