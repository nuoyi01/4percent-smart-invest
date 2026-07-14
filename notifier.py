import requests
import os

class Notifier:
    def __init__(self, feishu_url=None, dingtalk_url=None):
        self.feishu_url = feishu_url or os.environ.get("FEISHU_WEBHOOK")
        self.dingtalk_url = dingtalk_url or os.environ.get("DINGTALK_WEBHOOK")

    def send_feishu(self, title, content):
        if not self.feishu_url:
            return False
            
        headers = {"Content-Type": "application/json"}
        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [[{"tag": "text", "text": content}]]
                    }
                }
            }
        }
        try:
            requests.post(self.feishu_url, json=payload, headers=headers, timeout=10)
            print(f"✅ [Notifier] 飞书推送成功")
            return True
        except Exception as e:
            print(f"❌ [Notifier] 飞书推送异常: {e}")
            return False

    def send_dingtalk(self, title, content):
        if not self.dingtalk_url:
            return False
            
        headers = {"Content-Type": "application/json"}
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"### {title}\n\n{content}"
            }
        }
        try:
            requests.post(self.dingtalk_url, json=payload, headers=headers, timeout=10)
            print(f"✅ [Notifier] 钉钉推送成功")
            return True
        except Exception as e:
            print(f"❌ [Notifier] 钉钉推送异常: {e}")
            return False

    def notify(self, title, content):
        f_res = self.send_feishu(title, content)
        d_res = self.send_dingtalk(title, content)
        if not f_res and not d_res:
            print("⚠️ [Notifier] 未配置任何有效推送渠道，推送失败。")
        return f_res or d_res
