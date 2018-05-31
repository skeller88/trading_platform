import pandas as pd


def read_backtest_files():
    """
    "kb" - kaiko backtest
    "lb" - lambda backtest

    Returns:

    """
    # Read backtest files
    kb_1 = '/Users/shanekeller/Documents/arbitrage_bot/data/backtest/backtest_results_kaiko_dec_jan_profit_threshold_1.0_order_pad_0.2.csv'
    lb_1 = '/Users/shanekeller/Documents/arbitrage_bot/data/backtest/backtest_results_feb_mar_profit_threshold_1.0_order_pad_0.2.csv'

    # Fixed some bugs, don't remember which ones :/
    kb_2 = '/Users/shanekeller/Documents/arbitrage_bot/data/backtest/backtest_results_kaiko_dec_jan_2_profit_threshold_1.0_order_pad_0.2.csv'
    lb_2 = '/Users/shanekeller/Documents/arbitrage_bot/data/backtest/backtest_results_feb_mar_2_profit_threshold_1.0_order_pad_0.2.csv'

    # Added deposit/transfer delay during rebalance step
    kb_dd = '/Users/shanekeller/Documents/arbitrage_bot/data/backtest/backtest_results_kaiko_dec_jan_dd_profit_threshold_1.0_order_pad_0.2.csv'
    lb_dd = '/Users/shanekeller/Documents/arbitrage_bot/data/backtest/backtest_results_feb_mar_dd_profit_threshold_1.0_order_pad_0.2.csv'

    # Fixed order padding bug in which unpadded buy and sell prices were being used to calculate profits
    lb_pd = '/Users/shanekeller/Documents/arbitrage_bot/data/backtest/backtest_results_feb_mar_w_padding_profit_threshold_1.0_order_pad_0.2.csv'

    # Added a minimum order base value to prevent arbitraging when I only have a little bit of funds.
    lb_mb = '/Users/shanekeller/Documents/arbitrage_bot/data/backtest/backtest_results_feb_mar_min_base_order_profit_threshold_1.0_order_pad_0.2.csv'

    # Change criteria for determining a profitable arbitrage
    lb_roi = '/Users/shanekeller/Documents/arbitrage_bot/data/backtest/backtest_results_feb_mar_roi.csv'

    return {
        'kb_1': kb_1,
        'kb_2': kb_2,
        'kb_dd': kb_dd,
        'lb_1': lb_1,
        'lb_2': lb_2,
        'lb_dd': lb_dd,
        'lb_pd': lb_pd,
        'lb_mb': lb_mb,
        'lb_roi': lb_roi
    }


def analyze_results(filename):
    df = pd.read_csv(filename)
    pdf = df[(df.arbitrages_executed > 5)]
    pdf = pdf[pdf.base != 'USDT']

    # estimate the profits over bh extrapolating over a year
    pdf['p_yr'] = pdf['arb_profits_over_bh'] * 365 / pdf['time_period_days']
    pdf['a_per_day'] = pdf['arbitrages_executed'] / pdf['time_period_days']
    pdf['a_per_day'] = pdf[pdf.a_per_day.notnull()]
    pdf.rename(columns={'arbitrages_executed': 'a_ex',
                        'arbitrages_skipped': 'a_sk',
                        'arb_profits_over_bh': 'a_p_over_bh',
                        'net_profit_percent_threshold': 'p_thresh',
                        'arb_return': 'a_ret',
                        'bh_return': 'bh_ret',
                        'arb_profits': 'a_p',
                        'bh_profits': 'bh_p',
                        'initial_base_capital': 'capital'
                        }, inplace=True)
    # rearrange columns
    cols = pdf.columns.tolist()
    # move "p_yr", "a_per_day", "capital" to front
    cols = cols[:2] + cols[-3:] + cols[2:-3]
    cols = cols[:5] + cols[-4:-2] + cols[5:-4] + cols[-2:]
    pdf = pdf[cols]
    pdf = pdf.sort_values(by='arb_alpha', ascending=False)
    return pdf


def corr_arb_alpha_arbs_ex(filename):
    """
    The number of arbitrages executed and arb alpha should be positively correlated.

    With improved testing and a few bug fixes, the correlation between number of arbitrages executed and arb alpha has
    increased. And after adding deposit delays, the correlation decreased. This makes sense and is very good validation.
    Args:
        filename:

    Returns:

    """
    pdf = pd.read_csv(filename)
    pdf = pdf[(pdf.arbitrages_executed > 5)]
    # USDT base arbitrages aren't arbitrage-able because USDT withdrawal fees are so high
    pdf = pdf[pdf.base != 'USDT']
    return pdf.arb_alpha.corr(pdf.arbitrages_executed)