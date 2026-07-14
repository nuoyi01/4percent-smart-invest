import subprocess
from data_fetcher import DataFetcher
from strategy_engine import StrategyEngine
from state_manager import StateManager
from notifier import Notifier

def git_commit_and_push(files_to_commit):
    """自动将更新后的状态提交回 GitHub 仓库"""
    try:
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Action Bot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            print(" -> 今日无数据更新，无需提交代码。")
            return
            
        for file in files_to_commit:
            subprocess.run(["git", "add", file], check=True)
        subprocess.run(["git", "commit", "-m", "🤖 auto: 4%定投策略巡检，更新持仓状态"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 [Git] 状态已同步至 GitHub 仓库。")
    except Exception as e:
        print(f"❌ [Git] 自动提交失败: {e}")

def main():
    sm = StateManager()
    df = DataFetcher()
    
    # 优先从环境变量读取，也可以从 config 中扩展
    nt = Notifier(
        feishu_url=os.environ.get("FEISHU_WEBHOOK"),
        dingtalk_url=os.environ.get("DINGTALK_WEBHOOK")
    )

    config = sm.load_config()
    state = sm.load_state()

    has_changed = False
    updated_fund_states = []

    for fund_config in config.get('target_funds', []):
        name = fund_config['name']
        code = fund_config['code']

        # 查找或初始化基金状态
        fund_state = next((item for item in state.get('fund_states', []) if item['code'] == code), None)
        if not fund_state:
            fund_state = {
                "code": code,
                "name": name,
                "last_buy_price": None,
                "invested_shares": 0,
                "total_invested_amount": 0,
                "average_cost": 0,
                "highest_price_since_last_buy": 0,
                "current_phase": "未开始"
            }
            if 'fund_states' not in state:
                state['fund_states'] = []
            state['fund_states'].append(fund_state)
            has_changed = True

        print(f"\n======== 巡检中: {name} ({code}) ========")
        
        current_price = df.get_current_price(code)
        if not current_price:
            print(f"⚠️ 无法获取 {name} 的当前价格，跳过。")
            updated_fund_states.append(fund_state)
            continue

        print(f"   当前价格: {current_price}")
        
        strategy = StrategyEngine(fund_config, fund_state)
        signals = strategy.calculate_signals(current_price)

        if signals["action"]:
            print(f"   📢 触发信号: {signals['action']}")
            nt.notify(f"【4%定投法】{name} 交易信号", signals["message"])
            has_changed = True
        else:
            print("   ✅ 运行正常，未触及信号。")
        
        updated_fund_states.append(fund_state)

    state['fund_states'] = updated_fund_states

    if has_changed:
        sm.save_state(state)
        # 如果在 GitHub Actions 中运行，会自动提交
        # git_commit_and_push(['state.json'])
    else:
        print("\n✨ 今日无持仓状态变动。")

if __name__ == "__main__":
    main()
