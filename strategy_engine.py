
class StrategyEngine:
    """
    4% 定投法（强化版）核心策略引擎
    """
    def __init__(self, fund_config, fund_state):
        self.config = fund_config
        self.state = fund_state

    def calculate_signals(self, current_price):
        signals = {
            "buy": False,
            "sell": False,
            "message": "",
            "action": None
        }

        # 1. 建仓期逻辑 (首笔入场)
        if self.state.get("invested_shares", 0) == 0:
            signals["buy"] = True
            signals["action"] = "INITIAL_BUY"
            signals["message"] = f"【建仓期】首次买入 {self.config['name']} ({self.config['code']})，当前价格 {current_price}。"
            
            # 更新状态
            self.state["last_buy_price"] = current_price
            self.state["invested_shares"] = 1
            self.state["total_invested_amount"] = self.config["initial_investment_per_share"]
            self.state["average_cost"] = current_price
            self.state["highest_price_since_last_buy"] = current_price
            self.state["current_phase"] = "加仓期"
            return signals

        # 获取当前状态
        last_buy_price = self.state["last_buy_price"]
        invested_shares = self.state["invested_shares"]
        average_cost = self.state["average_cost"]
        highest_price_since_last_buy = self.state.get("highest_price_since_last_buy", current_price)
        current_phase = self.state.get("current_phase", "加仓期")

        # 更新持仓期间的最高价 (用于止盈回撤计算)
        if current_price > highest_price_since_last_buy:
            self.state["highest_price_since_last_buy"] = current_price
            highest_price_since_last_buy = current_price

        # 2. 加仓期逻辑 (买跌不买涨)
        if current_phase == "加仓期" and invested_shares < self.config["max_shares"]:
            # 只有跌破上一次买入点的 4% 才加仓
            buy_trigger_price = round(last_buy_price * 0.96, 4)
            if current_price <= buy_trigger_price:
                signals["buy"] = True
                signals["action"] = "ADD_POSITION"
                signals["message"] = f"【加仓期】{self.config['name']} 当前价 {current_price} 已跌破上次买入价 {last_buy_price} 的 4% 触发点 {buy_trigger_price}。建议买入第 {invested_shares + 1} 份。"
                
                # 更新状态
                self.state["last_buy_price"] = current_price
                self.state["invested_shares"] += 1
                self.state["total_invested_amount"] += self.config["initial_investment_per_share"]
                self.state["average_cost"] = self.state["total_invested_amount"] / self.state["invested_shares"]
                self.state["highest_price_since_last_buy"] = current_price # 加仓后重置最高价锚点
                return signals

        # 3. 止盈逻辑
        if invested_shares > 0:
            # 计算当前收益率 (基于平均成本)
            profit_rate = (current_price - average_cost) / average_cost
            
            # 3.1 止盈观察信号：涨幅超过平均成本 15%
            if current_phase == "加仓期" and profit_rate >= 0.15:
                self.state["current_phase"] = "止盈观察期"
                signals["message"] = f"【止盈观察】{self.config['name']} 当前收益率 {profit_rate:.2%} 已超过 15%，进入止盈观察区间。当前最高价锚点: {highest_price_since_last_buy}。"
                # 这里不触发 buy/sell，只是状态变更，但可以发个通知
                signals["action"] = "ENTER_PROFIT_OBSERVATION"
                return signals

            # 3.2 动态止盈信号：进入观察期后，从最高点回撤 4% 卖出
            if current_phase == "止盈观察期":
                sell_trigger_price = round(highest_price_since_last_buy * 0.96, 4)
                if current_price <= sell_trigger_price:
                    signals["sell"] = True
                    signals["action"] = "TAKE_PROFIT"
                    signals["message"] = f"【止盈离场】{self.config['name']} 当前价 {current_price} 从最高点 {highest_price_since_last_buy} 回撤已达 4% (触发价 {sell_trigger_price})。建议全部卖出止盈！"
                    
                    # 重置状态，准备下一轮循环
                    self.state["last_buy_price"] = None
                    self.state["invested_shares"] = 0
                    self.state["total_invested_amount"] = 0
                    self.state["average_cost"] = 0
                    self.state["highest_price_since_last_buy"] = 0
                    self.state["current_phase"] = "已止盈"
                    return signals

        return signals
