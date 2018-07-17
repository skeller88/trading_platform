from trading_platform.exchanges.data.enums import exchange_names

binance = 0
bittrex = 1
gdax = 2
kraken = 3
poloniex = 4
kucoin = 5
gemini = 6
bitflyer = 7
coinbase = 8

names_to_ids = {
    exchange_names.binance: binance,
    exchange_names.bitflyer: bitflyer,
    exchange_names.bittrex: bittrex,
    exchange_names.coinbase: coinbase,
    exchange_names.gdax: gdax,
    exchange_names.gemini: gemini,
    exchange_names.kraken: kraken,
    exchange_names.kucoin: kucoin,
    exchange_names.poloniex: poloniex,
}

all_ids = names_to_ids.values()

ids_to_names = { id: name for name, id in names_to_ids.items()}


def from_name(name):
    return names_to_ids.get(name)


def to_name(id):
    return ids_to_names.get(id)
