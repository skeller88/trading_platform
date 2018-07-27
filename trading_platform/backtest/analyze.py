import matplotlib.pyplot as plt
import pandas


def plot_vs_bh(backtest_filename: str, field, x_tick_freq: int):
    df: pandas.DataFrame = pandas.read_csv(backtest_filename)
    df['summary_datetime_dt'] = pandas.to_datetime(df.summary_datetime)
    ax = df.plot(figsize=(15, 4), x='summary_datetime', y=['bh_{0}'.format(field), field])
    ax.set_xticks(df.index[::x_tick_freq])
    ax.set_xticklabels(df.summary_datetime_dt.dt.strftime('%D')[::x_tick_freq], rotation=90)
    plt.show()