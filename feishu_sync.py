import requests
import os
import json

class FeishuSync:
    def __init__(self):
        self.app_id = os.environ.get("FEISHU_APP_ID")
        self.app_secret = os.environ.get("FEISHU_APP_SECRET")
        self.base_token = "BWz7blHtfazUdRsPtvDcifMbnub"
        self.table_id = None # 动态获取第一个数据表
        self.tenant_access_token = None

    def get_token(self):
        """获取飞书租户访问凭证"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        try:
            res = requests.post(url, json=payload).json()
            if res.get("code") == 0:
                self.tenant_access_token = res.get("tenant_access_token")
                return True
            print(f"❌ [飞书同步] 获取 Token 失败: {res.get('msg')}")
        except Exception as e:
            print(f"❌ [飞书同步] 获取 Token 异常: {e}")
        return False

    def get_table_id(self):
        """获取多维表格的第一个 Table ID"""
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_token}/tables"
        headers = {"Authorization": f"Bearer {self.tenant_access_token}"}
        try:
            res = requests.get(url, headers=headers).json()
            if res.get("code") == 0:
                tables = res.get("data", {}).get("items", [])
                if tables:
                    self.table_id = tables[0].get("table_id")
                    return True
            print(f"❌ [飞书同步] 获取 Table ID 失败: {res.get('msg')}")
        except Exception as e:
            print(f"❌ [飞书同步] 获取 Table ID 异常: {e}")
        return False

    def update_fund_data(self, fund_code, current_price, percentile, profit_rate=None):
        """更新指定基金的价格、估值及收益率"""
        if not self.tenant_access_token and not self.get_token(): return
        if not self.table_id and not self.get_table_id(): return

        # 1. 查找记录 ID
        search_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_token}/tables/{self.table_id}/records/search"
        headers = {"Authorization": f"Bearer {self.tenant_access_token}", "Content-Type": "application/json"}
        payload = {
            "filter": {
                "conjunction": "and",
                "conditions": [{"field_name": "代码", "operator": "is", "value": [fund_code]}]
            }
        }
        
        try:
            res = requests.post(search_url, headers=headers, json=payload).json()
            items = res.get("data", {}).get("items", [])
            if not items:
                print(f"⚠️ [飞书同步] 未找到代码为 {fund_code} 的记录")
                return

            record_id = items[0].get("record_id")
            
            # 2. 更新记录
            update_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_token}/tables/{self.table_id}/records/{record_id}"
            fields = {
                "当前价": current_price,
                "估值百分位": percentile
            }
            if profit_rate is not None:
                fields["收益率"] = profit_rate

            update_payload = {"fields": fields}
            update_res = requests.put(update_url, headers=headers, json=update_payload).json()
            if update_res.get("code") == 0:
                print(f"✅ [飞书同步] {fund_code} 数据已同步至看板")
            else:
                print(f"❌ [飞书同步] {fund_code} 更新失败: {update_res.get('msg')}")
        except Exception as e:
            print(f"❌ [飞书同步] 同步过程异常: {e}")

def sync_to_feishu(funds_data):
    """外部调用接口"""
    syncer = FeishuSync()
    if not syncer.app_id or not syncer.app_secret:
        print("ℹ️ [飞书同步] 未配置 FEISHU_APP_ID/SECRET，跳过看板同步。")
        return
    
    for fund in funds_data:
        syncer.update_fund_data(
            fund['code'], 
            fund['current_price'], 
            fund['percentile'], 
            fund.get('profit_rate')
        )
