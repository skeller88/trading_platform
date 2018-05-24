"""
Easy way to determine if a market exists for a particular exchange, rather than deal with exceptions for attempting to
get tickers for a market that doesn't exist.
"""
from exchanges.src.data.enums import exchange_ids

all_exchanges = {
    exchange_ids.binance : ['ETH/BTC', 'LTC/BTC', 'BNB/BTC', 'NEO/BTC', '123/456', 'QTUM/ETH', 'EOS/ETH', 'SNT/ETH', 'BNT/ETH', 'BCH/BTC', 'GAS/BTC', 'BNB/ETH', 'BTC/USDT', 'ETH/USDT', 'HSR/BTC', 'OAX/ETH', 'DNT/ETH', 'MCO/ETH', 'ICN/ETH', 'MCO/BTC', 'WTC/BTC', 'WTC/ETH', 'LRC/BTC', 'LRC/ETH', 'QTUM/BTC', 'YOYO/BTC', 'OMG/BTC', 'OMG/ETH', 'ZRX/BTC', 'ZRX/ETH', 'STRAT/BTC', 'STRAT/ETH', 'SNGLS/BTC', 'SNGLS/ETH', 'BQX/BTC', 'BQX/ETH', 'KNC/BTC', 'KNC/ETH', 'FUN/BTC', 'FUN/ETH', 'SNM/BTC', 'SNM/ETH', 'NEO/ETH', 'IOTA/BTC', 'IOTA/ETH', 'LINK/BTC', 'LINK/ETH', 'XVG/BTC', 'XVG/ETH', 'CTR/BTC', 'CTR/ETH', 'SALT/BTC', 'SALT/ETH', 'MDA/BTC', 'MDA/ETH', 'MTL/BTC', 'MTL/ETH', 'SUB/BTC', 'SUB/ETH', 'EOS/BTC', 'SNT/BTC', 'ETC/ETH', 'ETC/BTC', 'MTH/BTC', 'MTH/ETH', 'ENG/BTC', 'ENG/ETH', 'DNT/BTC', 'ZEC/BTC', 'ZEC/ETH', 'BNT/BTC', 'AST/BTC', 'AST/ETH', 'DASH/BTC', 'DASH/ETH', 'OAX/BTC', 'ICN/BTC', 'BTG/BTC', 'BTG/ETH', 'EVX/BTC', 'EVX/ETH', 'REQ/BTC', 'REQ/ETH', 'VIB/BTC', 'VIB/ETH', 'HSR/ETH', 'TRX/BTC', 'TRX/ETH', 'POWR/BTC', 'POWR/ETH', 'ARK/BTC', 'ARK/ETH', 'YOYO/ETH', 'XRP/BTC', 'XRP/ETH', 'MOD/BTC', 'MOD/ETH', 'ENJ/BTC', 'ENJ/ETH', 'STORJ/BTC', 'STORJ/ETH', 'BNB/USDT', 'VEN/BNB', 'YOYO/BNB', 'POWR/BNB', 'VEN/BTC', 'VEN/ETH', 'KMD/BTC', 'KMD/ETH', 'NULS/BNB', 'RCN/BTC', 'RCN/ETH', 'RCN/BNB', 'NULS/BTC', 'NULS/ETH', 'RDN/BTC', 'RDN/ETH', 'RDN/BNB', 'XMR/BTC', 'XMR/ETH', 'DLT/BNB', 'WTC/BNB', 'DLT/BTC', 'DLT/ETH', 'AMB/BTC', 'AMB/ETH', 'AMB/BNB', 'BCH/ETH', 'BCH/USDT', 'BCH/BNB', 'BAT/BTC', 'BAT/ETH', 'BAT/BNB', 'BCPT/BTC', 'BCPT/ETH', 'BCPT/BNB', 'ARN/BTC', 'ARN/ETH', 'GVT/BTC', 'GVT/ETH', 'CDT/BTC', 'CDT/ETH', 'GXS/BTC', 'GXS/ETH', 'NEO/USDT', 'NEO/BNB', 'POE/BTC', 'POE/ETH', 'QSP/BTC', 'QSP/ETH', 'QSP/BNB', 'BTS/BTC', 'BTS/ETH', 'BTS/BNB', 'XZC/BTC', 'XZC/ETH', 'XZC/BNB', 'LSK/BTC', 'LSK/ETH', 'LSK/BNB', 'TNT/BTC', 'TNT/ETH', 'FUEL/BTC', 'FUEL/ETH', 'MANA/BTC', 'MANA/ETH', 'BCD/BTC', 'BCD/ETH', 'DGD/BTC', 'DGD/ETH', 'IOTA/BNB', 'ADX/BTC', 'ADX/ETH', 'ADX/BNB', 'ADA/BTC', 'ADA/ETH', 'PPT/BTC', 'PPT/ETH', 'CMT/BTC', 'CMT/ETH', 'CMT/BNB', 'XLM/BTC', 'XLM/ETH', 'XLM/BNB', 'CND/BTC', 'CND/ETH', 'CND/BNB', 'LEND/BTC', 'LEND/ETH', 'WABI/BTC', 'WABI/ETH', 'WABI/BNB', 'LTC/ETH', 'LTC/USDT', 'LTC/BNB', 'TNB/BTC', 'TNB/ETH', 'WAVES/BTC', 'WAVES/ETH', 'WAVES/BNB', 'GTO/BTC', 'GTO/ETH', 'GTO/BNB', 'ICX/BTC', 'ICX/ETH', 'ICX/BNB', 'OST/BTC', 'OST/ETH', 'OST/BNB', 'ELF/BTC', 'ELF/ETH', 'AION/BTC', 'AION/ETH', 'AION/BNB', 'NEBL/BTC', 'NEBL/ETH', 'NEBL/BNB', 'BRD/BTC', 'BRD/ETH', 'BRD/BNB', 'MCO/BNB', 'EDO/BTC', 'EDO/ETH', 'WINGS/BTC', 'WINGS/ETH', 'NAV/BTC', 'NAV/ETH', 'NAV/BNB', 'LUN/BTC', 'LUN/ETH', 'TRIG/BTC', 'TRIG/ETH', 'TRIG/BNB'],
    exchange_ids.bittrex : ['1ST/BTC', '2GIVE/BTC', 'ABY/BTC', 'ADA/BTC', 'ADT/BTC', 'ADX/BTC', 'AEON/BTC', 'AGRS/BTC', 'AMP/BTC', 'ANT/BTC', 'APX/BTC', 'ARDR/BTC', 'ARK/BTC', 'AUR/BTC', 'BAT/BTC', 'BAY/BTC', 'BCH/BTC', 'BCY/BTC', 'BITB/BTC', 'BLITZ/BTC', 'BLK/BTC', 'BLOCK/BTC', 'BNT/BTC', 'BRK/BTC', 'BRX/BTC', 'BSD/BTC', 'BTCD/BTC', 'BTG/BTC', 'BURST/BTC', 'BYC/BTC', 'CANN/BTC', 'CFI/BTC', 'CLAM/BTC', 'CLOAK/BTC', 'CLUB/BTC', 'COVAL/BTC', 'CPC/BTC', 'CRB/BTC', 'CRW/BTC', 'CURE/BTC', 'CVC/BTC', 'DASH/BTC', 'DCR/BTC', 'DCT/BTC', 'DGB/BTC', 'DGD/BTC', 'DMD/BTC', 'DNT/BTC', 'DOGE/BTC', 'DOPE/BTC', 'DTB/BTC', 'DYN/BTC', 'EBST/BTC', 'EDG/BTC', 'EFL/BTC', 'EGC/BTC', 'EMC/BTC', 'EMC2/BTC', 'ENG/BTC', 'ENRG/BTC', 'ERC/BTC', 'ETC/BTC', 'ETH/BTC', 'EXCL/BTC', 'EXP/BTC', 'FAIR/BTC', 'FCT/BTC', 'FLDC/BTC', 'FLO/BTC', 'FTC/BTC', 'FUN/BTC', 'GAM/BTC', 'GAME/BTC', 'GBG/BTC', 'GBYTE/BTC', 'GCR/BTC', 'GEO/BTC', 'GLD/BTC', 'GNO/BTC', 'GNT/BTC', 'GOLOS/BTC', 'GRC/BTC', 'GRS/BTC', 'GUP/BTC', 'HMQ/BTC', 'INCNT/BTC', 'INFX/BTC', 'IOC/BTC', 'ION/BTC', 'IOP/BTC', 'KMD/BTC', 'KORE/BTC', 'LBC/BTC', 'LGD/BTC', 'LMC/BTC', 'LSK/BTC', 'LTC/BTC', 'LUN/BTC', 'MAID/BTC', 'MANA/BTC', 'MCO/BTC', 'MEME/BTC', 'MER/BTC', 'MLN/BTC', 'MONA/BTC', 'MTL/BTC', 'MUE/BTC', 'MUSIC/BTC', 'MYST/BTC', 'NAV/BTC', 'NBT/BTC', 'NEO/BTC', 'NEOS/BTC', 'NLG/BTC', 'NMR/BTC', 'NXC/BTC', 'NXS/BTC', 'NXT/BTC', 'OK/BTC', 'OMG/BTC', 'OMNI/BTC', 'PART/BTC', 'PAY/BTC', 'PDC/BTC', 'PINK/BTC', 'PIVX/BTC', 'PKB/BTC', 'POT/BTC', 'POWR/BTC', 'PPC/BTC', 'PTC/BTC', 'PTOY/BTC', 'QRL/BTC', 'QTUM/BTC', 'QWARK/BTC', 'RADS/BTC', 'RBY/BTC', 'RCN/BTC', 'RDD/BTC', 'REP/BTC', 'RISE/BTC', 'RLC/BTC', 'SALT/BTC', 'SBD/BTC', 'SC/BTC', 'SEQ/BTC', 'SHIFT/BTC', 'SIB/BTC', 'SLR/BTC', 'SLS/BTC', 'SNRG/BTC', 'SNT/BTC', 'SPHR/BTC', 'SPR/BTC', 'START/BTC', 'STEEM/BTC', 'STORJ/BTC', 'STRAT/BTC', 'SWIFT/BTC', 'SWT/BTC', 'SYNX/BTC', 'SYS/BTC', 'THC/BTC', 'TIX/BTC', 'TKS/BTC', 'TRIG/BTC', 'TRST/BTC', 'TRUST/BTC', 'TX/BTC', 'UBQ/BTC', 'UKG/BTC', 'UNB/BTC', 'VIA/BTC', 'VIB/BTC', 'VOX/BTC', 'VRC/BTC', 'VRM/BTC', 'VTC/BTC', 'VTR/BTC', 'WAVES/BTC', 'WINGS/BTC', 'XCP/BTC', 'XDN/BTC', 'XEL/BTC', 'XEM/BTC', 'XLM/BTC', 'XMG/BTC', 'XMR/BTC', 'XMY/BTC', 'XRP/BTC', 'XST/BTC', 'XVC/BTC', 'XVG/BTC', 'XWC/BTC', 'XZC/BTC', 'ZCL/BTC', 'ZEC/BTC', 'ZEN/BTC', '1ST/ETH', 'ADA/ETH', 'ADT/ETH', 'ADX/ETH', 'ANT/ETH', 'BAT/ETH', 'BCH/ETH', 'BNT/ETH', 'BTG/ETH', 'CFI/ETH', 'CRB/ETH', 'CVC/ETH', 'DASH/ETH', 'DGB/ETH', 'DGD/ETH', 'DNT/ETH', 'ENG/ETH', 'ETC/ETH', 'FCT/ETH', 'FUN/ETH', 'GNO/ETH', 'GNT/ETH', 'GUP/ETH', 'HMQ/ETH', 'LGD/ETH', 'LTC/ETH', 'LUN/ETH', 'MANA/ETH', 'MCO/ETH', 'MTL/ETH', 'MYST/ETH', 'NEO/ETH', 'NMR/ETH', 'OMG/ETH', 'PAY/ETH', 'POWR/ETH', 'PTOY/ETH', 'QRL/ETH', 'QTUM/ETH', 'RCN/ETH', 'REP/ETH', 'RLC/ETH', 'SALT/ETH', 'SC/ETH', 'SNT/ETH', 'STORJ/ETH', 'STRAT/ETH', 'TIX/ETH', 'TRST/ETH', 'UKG/ETH', 'VIB/ETH', 'WAVES/ETH', 'WINGS/ETH', 'XEM/ETH', 'XLM/ETH', 'XMR/ETH', 'XRP/ETH', 'ZEC/ETH', 'ADA/USDT', 'BCH/USDT', 'BTC/USDT', 'BTG/USDT', 'DASH/USDT', 'ETC/USDT', 'ETH/USDT', 'LTC/USDT', 'NEO/USDT', 'NXT/USDT', 'OMG/USDT', 'XMR/USDT', 'XRP/USDT', 'XVG/USDT', 'ZEC/USDT'],
    exchange_ids.gdax : ['BCH/USD', 'LTC/EUR', 'LTC/USD', 'LTC/BTC', 'ETH/EUR', 'ETH/USD', 'ETH/BTC', 'BTC/GBP', 'BTC/EUR', 'BTC/USD'],
    exchange_ids.kraken : ['BCH/EUR', 'BCH/USD', 'BCH/BTC', 'DASH/EUR', 'DASH/USD', 'DASH/BTC', 'EOS/ETH', 'EOS/BTC', 'GNO/ETH', 'GNO/BTC', 'USDT/USD', 'ETC/ETH', 'ETC/BTC', 'ETC/EUR', 'ETC/USD', 'ETH/BTC', 'ETHXBT.d', 'ETH/CAD', 'ETHCAD.d', 'ETH/EUR', 'ETHEUR.d', 'ETH/GBP', 'ETHGBP.d', 'ETH/JPY', 'ETHJPY.d', 'ETH/USD', 'ETHUSD.d', 'ICN/ETH', 'ICN/BTC', 'LTC/BTC', 'LTC/EUR', 'LTC/USD', 'MLN/ETH', 'MLN/BTC', 'REP/ETH', 'REP/BTC', 'REP/EUR', 'BTC/CAD', 'XBTCAD.d', 'BTC/EUR', 'XBTEUR.d', 'BTC/GBP', 'XBTGBP.d', 'BTC/JPY', 'XBTJPY.d', 'BTC/USD', 'XBTUSD.d', 'XDG/BTC', 'XLM/BTC', 'XMR/BTC', 'XMR/EUR', 'XMR/USD', 'XRP/BTC', 'XRP/EUR', 'XRP/USD', 'ZEC/BTC', 'ZEC/EUR', 'ZEC/USD', 'XLM/EUR'],
    exchange_ids.poloniex : ['BCN/BTC', 'BELA/BTC', 'BLK/BTC', 'BTCD/BTC', 'Bitmark/BTC', 'BTS/BTC', 'BURST/BTC', 'CLAM/BTC', 'DASH/BTC', 'DGB/BTC', 'DOGE/BTC', 'EMC2/BTC', 'FLDC/BTC', 'FLO/BTC', 'GAME/BTC', 'GRC/BTC', 'HUC/BTC', 'LTC/BTC', 'MAID/BTC', 'OMNI/BTC', 'NAV/BTC', 'NEOS/BTC', 'NMC/BTC', 'NXT/BTC', 'PINK/BTC', 'POT/BTC', 'PPC/BTC', 'RIC/BTC', 'STR/BTC', 'SYS/BTC', 'VIA/BTC', 'XVC/BTC', 'VRC/BTC', 'VTC/BTC', 'XBC/BTC', 'XCP/BTC', 'XEM/BTC', 'XMR/BTC', 'XPM/BTC', 'XRP/BTC', 'BTC/USDT', 'DASH/USDT', 'LTC/USDT', 'NXT/USDT', 'STR/USDT', 'XMR/USDT', 'XRP/USDT', 'BCN/XMR', 'BLK/XMR', 'BTCD/XMR', 'DASH/XMR', 'LTC/XMR', 'MAID/XMR', 'NXT/XMR', 'ETH/BTC', 'ETH/USDT', 'SC/BTC', 'BCY/BTC', 'EXP/BTC', 'FCT/BTC', 'RADS/BTC', 'AMP/BTC', 'DCR/BTC', 'LSK/BTC', 'LSK/ETH', 'LBC/BTC', 'STEEM/BTC', 'STEEM/ETH', 'SBD/BTC', 'ETC/BTC', 'ETC/ETH', 'ETC/USDT', 'REP/BTC', 'REP/USDT', 'REP/ETH', 'ARDR/BTC', 'ZEC/BTC', 'ZEC/ETH', 'ZEC/USDT', 'ZEC/XMR', 'STRAT/BTC', 'NXC/BTC', 'PASC/BTC', 'GNT/BTC', 'GNT/ETH', 'GNO/BTC', 'GNO/ETH', 'BCH/BTC', 'BCH/ETH', 'BCH/USDT', 'ZRX/BTC', 'ZRX/ETH', 'CVC/BTC', 'CVC/ETH', 'OMG/BTC', 'OMG/ETH', 'GAS/BTC', 'GAS/ETH', 'STORJ/BTC']
}