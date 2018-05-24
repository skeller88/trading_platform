"""
Run to populate the core.constants.exchange_markets values, so the exchanges don't have to be queried on every lambda
execution for a variable that doesn't change often.
"""
import exchanges.src.live.live_subclasses as exchange_subclasses

for subclass in exchange_subclasses.all_live():
    print(subclass.name())
    exchange_service = subclass(None, None)
    print(exchange_service.fetch_market_symbols())
    print('\n')