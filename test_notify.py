import os
from notifier import Notifier

def test():
    # 使用用户提供的 Webhook 地址进行测试
    feishu = "https://open.feishu.cn/open-apis/bot/v2/hook/25995796-b586-4df7-a80c-c4f59f495f49"
    dingtalk = "https://oapi.dingtalk.com/robot/send?access_token=ab4ca904d9af5b42cf60349386a01df5458fb2e90f6724ef45148aef3abb35e3"
    
    nt = Notifier(feishu_url=feishu, dingtalk_url=dingtalk)
    
    print("正在测试多渠道推送...")
    nt.notify("【4%定投法】测试通知", "这是一条来自 Manus 自动化脚本的测试消息，如果您收到了，说明飞书和钉钉配置成功！")

if __name__ == "__main__":
    test()
