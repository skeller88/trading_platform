import pandas

binance_withdrawal_fees_df = pandas.DataFrame(data=[
    {'currency': 'ADA', 'withdrawal_fee': 1.000000000000000},
    {'currency': 'ADX', 'withdrawal_fee': 4.100000000000000},
    {'currency': 'AE', 'withdrawal_fee': 1.400000000000000},
    {'currency': 'AION', 'withdrawal_fee': 1.100000000000000},
    {'currency': 'AMB', 'withdrawal_fee': 6.100000000000000},
    {'currency': 'APPC', 'withdrawal_fee': 6.900000000000000},
    {'currency': 'ARK', 'withdrawal_fee': 0.100000000000000},
    {'currency': 'ARN', 'withdrawal_fee': 2.100000000000000},
    {'currency': 'AST', 'withdrawal_fee': 7.700000000000000},
    {'currency': 'BAT', 'withdrawal_fee': 10.000000000000000},
    {'currency': 'BCC', 'withdrawal_fee': 0.001000000000000},
    {'currency': 'BCD', 'withdrawal_fee': 1.000000000000000},
    {'currency': 'BCPT', 'withdrawal_fee': 7.200000000000000},
    {'currency': 'BCX', 'withdrawal_fee': 0.500000000000000},
    {'currency': 'BLZ', 'withdrawal_fee': 7.800000000000000},
    {'currency': 'BNB', 'withdrawal_fee': 0.280000000000000},
    {'currency': 'BNT', 'withdrawal_fee': 0.900000000000000},
    {'currency': 'BRD', 'withdrawal_fee': 5.500000000000000},
    {'currency': 'BTC', 'withdrawal_fee': 0.000500000000000},
    {'currency': 'BTG', 'withdrawal_fee': 0.001000000000000},
    {'currency': 'BTM', 'withdrawal_fee': 5.000000000000000},
    {'currency': 'BTS', 'withdrawal_fee': 1.000000000000000},
    {'currency': 'CDT', 'withdrawal_fee': 68.000000000000000},
    {'currency': 'CHAT', 'withdrawal_fee': 32.600000000000000},
    {'currency': 'CLOAK', 'withdrawal_fee': 0.020000000000000},
    {'currency': 'CMT', 'withdrawal_fee': 23.000000000000000},
    {'currency': 'CND', 'withdrawal_fee': 39.000000000000000},
    {'currency': 'CTR', 'withdrawal_fee': 35.000000000000000},
    {'currency': 'DASH', 'withdrawal_fee': 0.002000000000000},
    {'currency': 'DGD', 'withdrawal_fee': 0.020000000000000},
    {'currency': 'DLT', 'withdrawal_fee': 14.900000000000000},
    {'currency': 'DNT', 'withdrawal_fee': 42.000000000000000},
    {'currency': 'EDO', 'withdrawal_fee': 1.700000000000000},
    {'currency': 'ELF', 'withdrawal_fee': 3.400000000000000},
    {'currency': 'ENG', 'withdrawal_fee': 1.600000000000000},
    {'currency': 'ENJ', 'withdrawal_fee': 27.000000000000000},
    {'currency': 'EOS', 'withdrawal_fee': 0.300000000000000},
    {'currency': 'ETC', 'withdrawal_fee': 0.010000000000000},
    {'currency': 'ETH', 'withdrawal_fee': 0.010000000000000},
    {'currency': 'ETHOS', 'withdrawal_fee': 1.200000000000000},
    {'currency': 'EVX', 'withdrawal_fee': 2.500000000000000},
    {'currency': 'FUEL', 'withdrawal_fee': 42.000000000000000},
    {'currency': 'FUN', 'withdrawal_fee': 87.000000000000000},
    {'currency': 'GAS', 'withdrawal_fee': 0E-15},
    {'currency': 'GNT', 'withdrawal_fee': 6.700000000000000},
    {'currency': 'GRS', 'withdrawal_fee': 0.200000000000000},
    {'currency': 'GTO', 'withdrawal_fee': 7.000000000000000},
    {'currency': 'GVT', 'withdrawal_fee': 0.190000000000000},
    {'currency': 'GXS', 'withdrawal_fee': 0.300000000000000},
    {'currency': 'HCC', 'withdrawal_fee': 0.000500000000000},
    {'currency': 'HSR', 'withdrawal_fee': 0.000100000000000},
    {'currency': 'ICN', 'withdrawal_fee': 2.800000000000000},
    {'currency': 'ICX', 'withdrawal_fee': 1.000000000000000},
    {'currency': 'INS', 'withdrawal_fee': 2.100000000000000},
    {'currency': 'IOST', 'withdrawal_fee': 79.800000000000000},
    {'currency': 'KMD', 'withdrawal_fee': 0.002000000000000},
    {'currency': 'KNC', 'withdrawal_fee': 1.500000000000000},
    {'currency': 'LEND', 'withdrawal_fee': 55.000000000000000},
    {'currency': 'LINK', 'withdrawal_fee': 8.600000000000000},
    {'currency': 'LLT', 'withdrawal_fee': 67.800000000000000},
    {'currency': 'LRC', 'withdrawal_fee': 5.200000000000000},
    {'currency': 'LSK', 'withdrawal_fee': 0.100000000000000},
    {'currency': 'LTC', 'withdrawal_fee': 0.010000000000000},
    {'currency': 'LUN', 'withdrawal_fee': 0.310000000000000},
    {'currency': 'MANA', 'withdrawal_fee': 29.000000000000000},
    {'currency': 'MCO', 'withdrawal_fee': 0.340000000000000},
    {'currency': 'MDA', 'withdrawal_fee': 3.600000000000000},
    {'currency': 'MIOTA', 'withdrawal_fee': 0.500000000000000},
    {'currency': 'MOD', 'withdrawal_fee': 2.000000000000000},
    {'currency': 'MTH', 'withdrawal_fee': 33.000000000000000},
    {'currency': 'MTL', 'withdrawal_fee': 0.900000000000000},
    {'currency': 'NANO', 'withdrawal_fee': 0.010000000000000},
    {'currency': 'NAV', 'withdrawal_fee': 0.200000000000000},
    {'currency': 'NCASH', 'withdrawal_fee': 96.500000000000000},
    {'currency': 'NEBL', 'withdrawal_fee': 0.010000000000000},
    {'currency': 'NEO', 'withdrawal_fee': 0E-15},
    {'currency': 'NULS', 'withdrawal_fee': 1.300000000000000},
    {'currency': 'OAX', 'withdrawal_fee': 5.300000000000000},
    {'currency': 'OMG', 'withdrawal_fee': 0.230000000000000},
    {'currency': 'ONT', 'withdrawal_fee': 0.100000000000000},
    {'currency': 'OST', 'withdrawal_fee': 17.000000000000000},
    {'currency': 'PIVX', 'withdrawal_fee': 0.020000000000000},
    {'currency': 'POA', 'withdrawal_fee': 0.010000000000000},
    {'currency': 'POE', 'withdrawal_fee': 73.000000000000000},
    {'currency': 'POWR', 'withdrawal_fee': 7.400000000000000},
    {'currency': 'PPT', 'withdrawal_fee': 0.180000000000000},
    {'currency': 'QLC', 'withdrawal_fee': 1.000000000000000},
    {'currency': 'QSP', 'withdrawal_fee': 22.000000000000000},
    {'currency': 'QTUM', 'withdrawal_fee': 0.010000000000000},
    {'currency': 'RCN', 'withdrawal_fee': 29.000000000000000},
    {'currency': 'RDN', 'withdrawal_fee': 1.900000000000000},
    {'currency': 'REQ', 'withdrawal_fee': 15.200000000000000},
    {'currency': 'RLC', 'withdrawal_fee': 2.800000000000000},
    {'currency': 'REP', 'withdrawal_fee': 0.100000000000000},
    {'currency': 'RPX', 'withdrawal_fee': 1.000000000000000},
    {'currency': 'SALT', 'withdrawal_fee': 1.100000000000000},
    {'currency': 'SBTC', 'withdrawal_fee': 0.000500000000000},
    {'currency': 'SNGLS', 'withdrawal_fee': 42.000000000000000},
    {'currency': 'SNM', 'withdrawal_fee': 17.000000000000000},
    {'currency': 'SNT', 'withdrawal_fee': 29.000000000000000},
    {'currency': 'STEEM', 'withdrawal_fee': 0.010000000000000},
    {'currency': 'STORJ', 'withdrawal_fee': 3.500000000000000},
    {'currency': 'STORM', 'withdrawal_fee': 63.000000000000000},
    {'currency': 'STRAT', 'withdrawal_fee': 0.100000000000000},
    {'currency': 'SUB', 'withdrawal_fee': 5.400000000000000},
    {'currency': 'SYS', 'withdrawal_fee': 0.001000000000000},
    {'currency': 'TNB', 'withdrawal_fee': 83.000000000000000},
    {'currency': 'TNT', 'withdrawal_fee': 33.000000000000000},
    {'currency': 'TRIG', 'withdrawal_fee': 12.500000000000000},
    {'currency': 'TRX', 'withdrawal_fee': 53.000000000000000},
    {'currency': 'USDT', 'withdrawal_fee': 5.000000000000000},
    {'currency': 'VEN', 'withdrawal_fee': 1.100000000000000},
    {'currency': 'VIA', 'withdrawal_fee': 0.010000000000000},
    {'currency': 'VIB', 'withdrawal_fee': 19.000000000000000},
    {'currency': 'VIBE', 'withdrawal_fee': 13.300000000000000},
    {'currency': 'WABI', 'withdrawal_fee': 3.200000000000000},
    {'currency': 'WAN', 'withdrawal_fee': 0.100000000000000},
    {'currency': 'WAVES', 'withdrawal_fee': 0.002000000000000},
    {'currency': 'WINGS', 'withdrawal_fee': 6.800000000000000},
    {'currency': 'WPR', 'withdrawal_fee': 26.500000000000000},
    {'currency': 'WTC', 'withdrawal_fee': 0.300000000000000},
    {'currency': 'XEM', 'withdrawal_fee': 4.000000000000000},
    {'currency': 'XLM', 'withdrawal_fee': 0.010000000000000},
    {'currency': 'XMR', 'withdrawal_fee': 0.040000000000000},
    {'currency': 'XRP', 'withdrawal_fee': 0.250000000000000},
    {'currency': 'XVG', 'withdrawal_fee': 0.100000000000000},
    {'currency': 'XZC', 'withdrawal_fee': 0.020000000000000},
    {'currency': 'YOYOW', 'withdrawal_fee': 33.000000000000000},
    {'currency': 'ZEC', 'withdrawal_fee': 0.005000000000000},
    {'currency': 'ZEN','withdrawal_fee': 0.002000000000000},
    {'currency': 'ZIL', 'withdrawal_fee': 100.000000000000000},
    {'currency': 'ZRX', 'withdrawal_fee': 3.700000000000000}
])
binance_withdrawal_fees_df.set_index(keys='currency', inplace=True)

bittrex_withdrawal_fees_df = pandas.DataFrame(data=[
    {'currency': '1ST', 'withdrawal_fee': 4.500000000000000},
    {'currency': '2GIVE', 'withdrawal_fee': 0.010000000000000},
    {'currency': '8BIT', 'withdrawal_fee': 0.002000000000000},
    {'currency': 'ABY','withdrawal_fee': 0.200000000000000},
    {'currency': 'ADA','withdrawal_fee': 0.200000000000000},
    {'currency': 'ADC','withdrawal_fee': 2.000000000000000},
    {'currency': 'ADT','withdrawal_fee': 43.000000000000000},
    {'currency': 'ADX','withdrawal_fee': 3.000000000000000},
    {'currency': 'AEON','withdrawal_fee': 0.100000000000000},
    {'currency': 'AGRS','withdrawal_fee': 5.000000000000000},
    {'currency': 'AMP','withdrawal_fee': 5.000000000000000},
    {'currency': 'AMS','withdrawal_fee': 1.000000000000000},
    {'currency': 'ANT','withdrawal_fee': 1.300000000000000},
    {'currency': 'APX','withdrawal_fee': 0.100000000000000},
    {'currency': 'ARB','withdrawal_fee': 0.020000000000000},
    {'currency': 'ARDR','withdrawal_fee': 2.000000000000000},
    {'currency': 'ARK','withdrawal_fee': 0.100000000000000},
    {'currency': 'AUR','withdrawal_fee': 0.002000000000000},
    {'currency': 'BAT','withdrawal_fee': 10.000000000000000},
    {'currency': 'BAY','withdrawal_fee': 0.200000000000000},
    {'currency': 'BCC','withdrawal_fee': 0.001000000000000},
    {'currency': 'BCPT','withdrawal_fee': 1.000000000000000},
    {'currency': 'BCY','withdrawal_fee': 5.000000000000000},
    {'currency': 'BITB','withdrawal_fee': 0.200000000000000},
    {'currency': 'BITCNY','withdrawal_fee': 1.500000000000000},
    {'currency': 'BITS','withdrawal_fee': 0.002000000000000},
    {'currency': 'BITZ','withdrawal_fee': 0.020000000000000},
    {'currency': 'BLC','withdrawal_fee': 0.200000000000000},
    {'currency': 'BLITZ','withdrawal_fee': 0.020000000000000},
    {'currency': 'BLK','withdrawal_fee': 0.020000000000000},
    {'currency': 'BLOCK','withdrawal_fee': 0.020000000000000},
    {'currency': 'BNT','withdrawal_fee': 0.850000000000000},
    {'currency': 'BRK','withdrawal_fee': 0.020000000000000},
    {'currency': 'BRX','withdrawal_fee': 0.020000000000000},
    {'currency': 'BSD','withdrawal_fee': 0.002000000000000},
    {'currency': 'BSTY','withdrawal_fee': 0.200000000000000},
    {'currency': 'BTA','withdrawal_fee': 1.000000000000000},
    {'currency': 'BTC','withdrawal_fee': 0.000500000000000},
    {'currency': 'BTCD','withdrawal_fee': 0.020000000000000},
    {'currency': 'BTCP','withdrawal_fee': 0.010000000000000},
    {'currency': 'BTG','withdrawal_fee': 0.001000000000000},
    {'currency': 'BTS','withdrawal_fee': 5.000000000000000},
    {'currency': 'BURST','withdrawal_fee': 2.000000000000000},
    {'currency': 'BYC','withdrawal_fee': 0.020000000000000},
    {'currency': 'CANN','withdrawal_fee': 0.200000000000000},
    {'currency': 'CCN','withdrawal_fee': 0.020000000000000},
    {'currency': 'CFI','withdrawal_fee': 27.000000000000000},
    {'currency': 'CLAM','withdrawal_fee': 0.200000000000000},
    {'currency': 'CLOAK','withdrawal_fee': 0.020000000000000},
    {'currency': 'CLUB','withdrawal_fee': 0.020000000000000},
    {'currency': 'COVAL','withdrawal_fee': 200.000000000000000},
    {'currency': 'CPC','withdrawal_fee': 0.200000000000000},
    {'currency': 'CRB','withdrawal_fee': 8.000000000000000},
    {'currency': 'CRW','withdrawal_fee': 0.020000000000000},
    {'currency': 'CRYPT','withdrawal_fee': 0.020000000000000},
    {'currency': 'CURE','withdrawal_fee': 0.000200000000000},
    {'currency': 'CVC','withdrawal_fee': 8.000000000000000},
    {'currency': 'DAR','withdrawal_fee': 0.100000000000000},
    {'currency': 'DASH','withdrawal_fee': 0.002000000000000},
    {'currency': 'DCR','withdrawal_fee': 0.100000000000000},
    {'currency': 'DCT','withdrawal_fee': 0.100000000000000},
    {'currency': 'DGB','withdrawal_fee': 0.200000000000000},
    {'currency': 'DGC','withdrawal_fee': 0.200000000000000},
    {'currency': 'DGD','withdrawal_fee': 0.038000000000000},
    {'currency': 'DMD','withdrawal_fee': 0.002000000000000},
    {'currency': 'DMT','withdrawal_fee': 1.000000000000000},
    {'currency': 'DNT','withdrawal_fee': 29.000000000000000},
    {'currency': 'DOGE','withdrawal_fee': 2.000000000000000},
    {'currency': 'DOPE','withdrawal_fee': 0.002000000000000},
    {'currency': 'DTB','withdrawal_fee': 5.000000000000000},
    {'currency': 'DTC','withdrawal_fee': 0.200000000000000},
    {'currency': 'DYN','withdrawal_fee': 0.020000000000000},
    {'currency': 'EBST','withdrawal_fee': 0.100000000000000},
    {'currency': 'EDG','withdrawal_fee': 3.500000000000000},
    {'currency': 'EFL','withdrawal_fee': 0.200000000000000},
    {'currency': 'EGC','withdrawal_fee': 0.200000000000000},
    {'currency': 'EMC','withdrawal_fee': 0.020000000000000},
    {'currency': 'EMC2','withdrawal_fee': 0.200000000000000},
    {'currency': 'ENG','withdrawal_fee': 1.000000000000000},
    {'currency': 'ENRG','withdrawal_fee': 0.200000000000000},
    {'currency': 'ERC','withdrawal_fee': 0.200000000000000},
    {'currency': 'ETC','withdrawal_fee': 0.010000000000000},
    {'currency': 'ETH','withdrawal_fee': 0.006000000000000},
    {'currency': 'EXCL','withdrawal_fee': 0.200000000000000},
    {'currency': 'EXP','withdrawal_fee': 0.010000000000000},
    {'currency': 'FAIR','withdrawal_fee': 0.020000000000000},
    {'currency': 'FC2','withdrawal_fee': 0.020000000000000},
    {'currency': 'FCT','withdrawal_fee': 0.010000000000000},
    {'currency': 'FLDC','withdrawal_fee': 150.000000000000000},
    {'currency': 'FLO','withdrawal_fee': 0.200000000000000},
    {'currency': 'FRK','withdrawal_fee': 0.002000000000000},
    {'currency': 'FTC','withdrawal_fee': 0.200000000000000},
    {'currency': 'FUN','withdrawal_fee': 49.000000000000000},
    {'currency': 'GAM','withdrawal_fee': 0.300000000000000},
    {'currency': 'GAME','withdrawal_fee': 0.200000000000000},
    {'currency': 'GBG','withdrawal_fee': 0.010000000000000},
    {'currency': 'GBYTE','withdrawal_fee': 0.002000000000000},
    {'currency': 'GCR','withdrawal_fee': 0.020000000000000},
    {'currency': 'GEO','withdrawal_fee': 0.100000000000000},
    {'currency': 'GLD','withdrawal_fee': 0.000200000000000},
    {'currency': 'GNO','withdrawal_fee': 0.020000000000000},
    {'currency': 'GNT','withdrawal_fee': 9.000000000000000},
    {'currency': 'GOLOS','withdrawal_fee': 0.010000000000000},
    {'currency': 'GP','withdrawal_fee': 0.200000000000000},
    {'currency': 'GRC','withdrawal_fee': 0.200000000000000},
    {'currency': 'GRS','withdrawal_fee': 0.200000000000000},
    {'currency': 'GTO', 'withdrawal_fee': 1.000000000000000},
    {'currency': 'GRT','withdrawal_fee': 20.000000000000000},
    {'currency': 'GUP','withdrawal_fee': 7.000000000000000},
    {'currency': 'HMQ','withdrawal_fee': 16.000000000000000},
    {'currency': 'HYPER','withdrawal_fee': 0.020000000000000},
    {'currency': 'IGNIS','withdrawal_fee': 2.000000000000000},
    {'currency': 'INCNT','withdrawal_fee': 0.100000000000000},
    {'currency': 'INFX','withdrawal_fee': 0.100000000000000},
    {'currency': 'IOC','withdrawal_fee': 0.200000000000000},
    {'currency': 'ION','withdrawal_fee': 0.200000000000000},
    {'currency': 'IOP','withdrawal_fee': 0.200000000000000},
    {'currency': 'J','withdrawal_fee': 0.020000000000000},
    {'currency': 'KMD','withdrawal_fee': 0.002000000000000},
    {'currency': 'KORE','withdrawal_fee': 0.020000000000000},
    {'currency': 'LBC','withdrawal_fee': 0.020000000000000},
    {'currency': 'LGD','withdrawal_fee': 4.000000000000000},
    {'currency': 'LMC','withdrawal_fee': 0.200000000000000},
    {'currency': 'LRC','withdrawal_fee': 1.000000000000000},
    {'currency': 'LSK','withdrawal_fee': 0.100000000000000},
    {'currency': 'LTC','withdrawal_fee': 0.010000000000000},
    {'currency': 'LUN','withdrawal_fee': 0.150000000000000},
    {'currency': 'MAID','withdrawal_fee': 2.000000000000000},
    {'currency': 'MANA','withdrawal_fee': 36.000000000000000},
    {'currency': 'MAX','withdrawal_fee': 0.200000000000000},
    {'currency': 'MCO','withdrawal_fee': 0.500000000000000},
    {'currency': 'MEC','withdrawal_fee': 1.000000000000000},
    {'currency': 'MEME','withdrawal_fee': 0.020000000000000},
    {'currency': 'MER','withdrawal_fee': 0.100000000000000},
    {'currency': 'METAL','withdrawal_fee': 20.000000000000000},
    {'currency': 'MLN','withdrawal_fee': 0.035000000000000},
    {'currency': 'MND','withdrawal_fee': 1.000000000000000},
    {'currency': 'MONA','withdrawal_fee': 0.200000000000000},
    {'currency': 'MTL','withdrawal_fee': 1.350000000000000},
    {'currency': 'MUE','withdrawal_fee': 0.020000000000000},
    {'currency': 'MUSIC','withdrawal_fee': 0.010000000000000},
    {'currency': 'MYST','withdrawal_fee': 2.500000000000000},
    {'currency': 'MZC','withdrawal_fee': 0.200000000000000},
    {'currency': 'NAV','withdrawal_fee': 0.200000000000000},
    {'currency': 'NEO','withdrawal_fee': 0.025000000000000},
    {'currency': 'NEOS','withdrawal_fee': 0.020000000000000},
    {'currency': 'NET','withdrawal_fee': 0.200000000000000},
    {'currency': 'NEU','withdrawal_fee': 0.020000000000000},
    {'currency': 'NLG','withdrawal_fee': 0.200000000000000},
    {'currency': 'NMR','withdrawal_fee': 0.150000000000000},
    {'currency': 'NTRN','withdrawal_fee': 0.020000000000000},
    {'currency': 'NXC','withdrawal_fee': 13.000000000000000},
    {'currency': 'NXS','withdrawal_fee': 0.200000000000000},
    {'currency': 'NXT','withdrawal_fee': 2.000000000000000},
    {'currency': 'OC','withdrawal_fee': 0.200000000000000},
    {'currency': 'OK','withdrawal_fee': 0.200000000000000},
    {'currency': 'OMG','withdrawal_fee': 0.350000000000000},
    {'currency': 'OMNI','withdrawal_fee': 0.100000000000000},
    {'currency': 'ORB','withdrawal_fee': 0.200000000000000},
    {'currency': 'PART','withdrawal_fee': 0.100000000000000},
    {'currency': 'PAY','withdrawal_fee': 2.000000000000000},
    {'currency': 'PDC','withdrawal_fee': 5.000000000000000},
    {'currency': 'PINK','withdrawal_fee': 0.200000000000000},
    {'currency': 'PIVX','withdrawal_fee': 0.020000000000000},
    {'currency': 'PKB','withdrawal_fee': 0.020000000000000},
    {'currency': 'POLY','withdrawal_fee': 1.000000000000000},
    {'currency': 'POT','withdrawal_fee': 0.002000000000000},
    {'currency': 'POWR','withdrawal_fee': 5.000000000000000},
    {'currency': 'PPC','withdrawal_fee': 0.020000000000000},
    {'currency': 'PRO','withdrawal_fee': 1.000000000000000},
    {'currency': 'PTC','withdrawal_fee': 0.002000000000000},
    {'currency': 'PTOY','withdrawal_fee': 14.000000000000000},
    {'currency': 'PXI','withdrawal_fee': 0.200000000000000},
    {'currency': 'QRL','withdrawal_fee': 2.500000000000000},
    {'currency': 'QTUM','withdrawal_fee': 0.010000000000000},
    {'currency': 'QWARK','withdrawal_fee': 0.100000000000000},
    {'currency': 'RADS','withdrawal_fee': 0.200000000000000},
    {'currency': 'RBY','withdrawal_fee': 0.020000000000000},
    {'currency': 'RCN','withdrawal_fee': 16.000000000000000},
    {'currency': 'RDD','withdrawal_fee': 2.000000000000000},
    {'currency': 'REP','withdrawal_fee': 0.100000000000000},
    {'currency': 'RISE','withdrawal_fee': 0.100000000000000},
    {'currency': 'RLC','withdrawal_fee': 3.500000000000000},
    {'currency': 'RVR','withdrawal_fee': 0.100000000000000},
    {'currency': 'SAFEX','withdrawal_fee': 100.000000000000000},
    {'currency': 'SALT','withdrawal_fee': 0.600000000000000},
    {'currency': 'SBD','withdrawal_fee': 0.010000000000000},
    {'currency': 'SC','withdrawal_fee': 0.100000000000000},
    {'currency': 'SCRT','withdrawal_fee': 1.000000000000000},
    {'currency': 'SEQ','withdrawal_fee': 0.200000000000000},
    {'currency': 'SHIFT','withdrawal_fee': 0.010000000000000},
    {'currency': 'SIB','withdrawal_fee': 0.200000000000000},
    {'currency': 'SLG','withdrawal_fee': 0.200000000000000},
    {'currency': 'SLING','withdrawal_fee': 0.002000000000000},
    {'currency': 'SLR','withdrawal_fee': 0.200000000000000},
    {'currency': 'SLS','withdrawal_fee': 0.002000000000000},
    {'currency': 'SNGLS','withdrawal_fee': 3.500000000000000},
    {'currency': 'SNRG','withdrawal_fee': 0.002000000000000},
    {'currency': 'SNT','withdrawal_fee': 20.000000000000000},
    {'currency': 'SOON','withdrawal_fee': 0.200000000000000},
    {'currency': 'SPHR','withdrawal_fee': 0.002000000000000},
    {'currency': 'SPR','withdrawal_fee': 0.200000000000000},
    {'currency': 'SPRTS','withdrawal_fee': 1.000000000000000},
    {'currency': 'SRN','withdrawal_fee': 1.000000000000000},
    {'currency': 'START','withdrawal_fee': 0.020000000000000},
    {'currency': 'STEEM','withdrawal_fee': 0.010000000000000},
    {'currency': 'STEPS','withdrawal_fee': 0.200000000000000},
    {'currency': 'STORJ','withdrawal_fee': 3.000000000000000},
    {'currency': 'STORM','withdrawal_fee': 1.000000000000000},
    {'currency': 'STRAT','withdrawal_fee': 0.200000000000000},
    {'currency': 'STV','withdrawal_fee': 0.200000000000000},
    {'currency': 'SWIFT','withdrawal_fee': 2.000000000000000},
    {'currency': 'SWING','withdrawal_fee': 0.100000000000000},
    {'currency': 'SWT','withdrawal_fee': 1.800000000000000},
    {'currency': 'SYNX','withdrawal_fee': 0.200000000000000},
    {'currency': 'SYS','withdrawal_fee': 0.000200000000000},
    {'currency': 'TES','withdrawal_fee': 0.200000000000000},
    {'currency': 'THC','withdrawal_fee': 0.200000000000000},
    {'currency': 'TIME','withdrawal_fee': 0.200000000000000},
    {'currency': 'TIT','withdrawal_fee': 0.200000000000000},
    {'currency': 'TIX','withdrawal_fee': 5.000000000000000},
    {'currency': 'TKN','withdrawal_fee': 0.400000000000000},
    {'currency': 'TKS','withdrawal_fee': 0.100000000000000},
    {'currency': 'TRI','withdrawal_fee': 0.000200000000000},
    {'currency': 'TRIG','withdrawal_fee': 5.000000000000000},
    {'currency': 'TRK','withdrawal_fee': 0.020000000000000},
    {'currency': 'TROLL','withdrawal_fee': 0.001000000000000},
    {'currency': 'TRST','withdrawal_fee': 7.000000000000000},
    {'currency': 'TRUST','withdrawal_fee': 0.020000000000000},
    {'currency': 'TRX','withdrawal_fee': 1.000000000000000},
    {'currency': 'TUSD','withdrawal_fee': 1.000000000000000},
    {'currency': 'TX','withdrawal_fee': 0.020000000000000},
    {'currency': 'UBQ','withdrawal_fee': 0.010000000000000},
    {'currency': 'UFO','withdrawal_fee': 0.200000000000000},
    {'currency': 'UKG','withdrawal_fee': 5.000000000000000},
    {'currency': 'UNB','withdrawal_fee': 0.200000000000000},
    {'currency': 'UNIT','withdrawal_fee': 2.000000000000000},
    {'currency': 'UNO','withdrawal_fee': 0.000200000000000},
    {'currency': 'UP','withdrawal_fee': 1.000000000000000},
    {'currency': 'USDT','withdrawal_fee': 25.000000000000000},
    {'currency': 'UTC','withdrawal_fee': 0.020000000000000},
    {'currency': 'VEE','withdrawal_fee': 1.000000000000000},
    {'currency': 'VIA','withdrawal_fee': 0.200000000000000},
    {'currency': 'VIB','withdrawal_fee': 13.000000000000000},
    {'currency': 'VOX','withdrawal_fee': 0.100000000000000},
    {'currency': 'VRC','withdrawal_fee': 0.000200000000000},
    {'currency': 'VRM','withdrawal_fee': 0.400000000000000},
    {'currency': 'VTC','withdrawal_fee': 0.020000000000000},
    {'currency': 'VTR','withdrawal_fee': 0.020000000000000},
    {'currency': 'WARP','withdrawal_fee': 0.020000000000000},
    {'currency': 'WAVES','withdrawal_fee': 0.001000000000000},
    {'currency': 'WAX','withdrawal_fee': 1.000000000000000},
    {'currency': 'WINGS','withdrawal_fee': 4.000000000000000},
    {'currency': 'XAUR','withdrawal_fee': 2.500000000000000},
    {'currency': 'XCO','withdrawal_fee': 0.020000000000000},
    {'currency': 'XCP','withdrawal_fee': 0.200000000000000},
    {'currency': 'XDN','withdrawal_fee': 0.010000000000000},
    {'currency': 'XEL','withdrawal_fee': 0.200000000000000},
    {'currency': 'XEM','withdrawal_fee': 4.000000000000000},
    {'currency': 'XLM','withdrawal_fee': 0.010000000000000},
    {'currency': 'XMG','withdrawal_fee': 0.000200000000000},
    {'currency': 'XMR','withdrawal_fee': 0.040000000000000},
    {'currency': 'XMY','withdrawal_fee': 0.200000000000000},
    {'currency': 'XPY','withdrawal_fee': 0.002000000000000},
    {'currency': 'XQN','withdrawal_fee': 0.020000000000000},
    {'currency': 'XRP','withdrawal_fee': 1.000000000000000},
    {'currency': 'XST','withdrawal_fee': 0.020000000000000},
    {'currency': 'XVC','withdrawal_fee': 0.002000000000000},
    {'currency': 'XVG','withdrawal_fee': 0.200000000000000},
    {'currency': 'XWC','withdrawal_fee': 0.200000000000000},
    {'currency': 'XZC','withdrawal_fee': 0.020000000000000},
    {'currency': 'ZCL','withdrawal_fee': 0.002000000000000},
    {'currency': 'ZEC','withdrawal_fee': 0.005000000000000},
    {'currency': 'ZEN','withdrawal_fee': 0.002000000000000},
    {'currency': 'ZRX','withdrawal_fee': 1.000000000000000}
])
bittrex_withdrawal_fees_df.set_index(keys='currency', inplace=True)