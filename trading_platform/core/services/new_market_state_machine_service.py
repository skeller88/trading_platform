from abc import ABC
from typing import Dict

from trading_platform.core.services.strategy_state_machine_service_abc import StrategyStateMachineServiceAbc
from trading_platform.exchanges.exchange_service_abc import ExchangeServiceAbc
from trading_platform.storage.daos.open_order_dao import OpenOrderDao
from trading_platform.storage.daos.order_dao import OrderDao


class NewMarketStrategyStateMachineService(StrategyStateMachineServiceAbc):
    def __init__(self, state_machine: Dict, logger, exchanges_by_id: Dict[int, ExchangeServiceAbc],
                 open_order_dao: OpenOrderDao, order_dao: OrderDao):
        super().__init__(state_machine=state_machine, logger=logger, exchanges_by_id=exchanges_by_id,
                         open_order_dao=open_order_dao, order_dao=order_dao)

    @StrategyStateMachineServiceAbc.state
    def buy_on_xchg(s):
        if not s.has["buy.order_id"]
            """
            This poll introduces latency. 
            A faster approach would risk reorder & have it fail due to either:
            1) Insufficient balance.
            2) Insufficient volume.
            """
            xchg = s.state["buy.xchg"]
            order = s.state["buy"]
            is_finding = True
            while is_finding
                sleep
                s.possibly_fail("before get buys")
                orders = xchg.get_orders()
                s.possibly_fail("after get buys")
                if order in orders
                    s.state["buy.order_id"] = order_id
                    s.new_state(watch_for_sell_signal)  # avoid redundant order
                if timed out
                break

        xchg = s.state["buy.xchg"]
        order = s.state["buy"]
        res = xchg.order(order)
        if fail
            retry()
        s.possibly_fail("after buy on xchg")
        s.state["buy.order_id"] = res.order_id

    s.new_state(verify_buy_on_xchg)


    @state
    def verify_buy_on_xchg(s):
        is_incomplete = True
        while is_incomplete  # alternative is to use retry()
            sleep
            order = xchg.get_order(s.state["buy.order_id"])
            if failure
                s.new_state(cant_find_buy)
            if order.is_complete
                s.new_state(watch_for_sell_signal)
            if timed out  # SM could enforce this
            s.new_state(cant_complete_buy)


    @state
    def cant_find_buy(s):


    @state
    cant_complete_buy(s):


    @state
    def watch_for_sell_signal(s):
        ...
        s.new_state(sell)


    @state
    def sell(s):
        # similar to buy_announced_market
        s.new_state(sell_on_xchg)


    @state
    def sell_on_xchg(s):
        # similar to buy_on_xchg
        s.new_state(verify_sell_on_xchg)


    @state
    def verify_sell_on_xchg(s):
        # similar to verify_buy_on_xchg
        s.new_state(archive_trade)


    @state
    def cant_find_sell(s):


    @state
    def cant_complete_sell(s):


    @state
    def archive_trade(s):
        # RDS
        begin_trans()
        if not sql()
            rollback()
            retry()
        if not commit()
            rollback()
            retry()
        s.new_state(watch_twit)
