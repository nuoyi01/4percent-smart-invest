import json
import requests
import akshare as ak
import re

class DataFetcher:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def get_price_from_akshare(self, code):
        """【主数据源】从 akshare 抓取 ETF 基金实时价格"""
        try:
            df = ak.fund_etf_spot_sine()
            row = df[df["代码"] == code]
            if not row.empty:
                price = float(row["最新价"].values[0])
                return price
            return None
        except Exception as e:
            print(f"   [数据源: AkShare] 报错: {e}")
            return None

    def get_price_from_sina(self, code):
        """【备选数据源1】从新浪财经抓取实时价格"""
        try:
            prefix = 'sh' if code.startswith('5') or code.startswith('6') else 'sz'
            url = f"http://hq.sinajs.cn/list={prefix}{code}"
            headers = {"Referer": "http://finance.sina.com.cn"}
            response = requests.get(url, headers=headers, timeout=5)
            data = response.text.split(',')
            if len(data) > 3:
                price = float(data[3])
                if price > 0:
                    return price
            return None
        except Exception as e:
            print(f"   [数据源: 新浪财经] 报错: {e}")
            return None

    def get_price_from_tiantian(self, code):
        """【备选数据源2】从天天基金 API 抓取实时估算净值"""
        try:
            url = f"http://fundgz.1234567.com.cn/js/{code}.js"
            response = requests.get(url, headers=self.headers, timeout=5)
            match = re.search(r"jsonpgz\((.*)\);", response.text)
            if match:
                json_data = json.loads(match.group(1))
                price = float(json_data["gsz"])
                return price
            return None
        except Exception as e:
            print(f"   [数据源: 天天基金] 报错: {e}")
            return None

    def get_current_price(self, code):
        """多源容错获取价格"""
        price = self.get_price_from_akshare(code)
        if price: return price
        
        price = self.get_price_from_sina(code)
        if price: return price
        
        price = self.get_price_from_tiantian(code)
        if price: return price
        
        return None
