import smtplib
import os
import time
import json
from email.mime.text import MIMEText
from email.header import Header

def send_email(subject, content):
    """通用邮件发送逻辑"""
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", 465))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    receivers = os.environ.get("ALERT_RECEIVER", "").split(",")

    if not all([smtp_host, smtp_user, smtp_pass, receivers]):
        print("❌ [邮件告警] SMTP 配置不完整，无法发送邮件。")
        return False

    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = smtp_user
    message['To'] = ",".join(receivers)
    message['Subject'] = Header(subject, 'utf-8')

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
        
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, receivers, message.as_string())
        server.quit()
        print(f"✅ [邮件告警] 邮件已发送至: {receivers}")
        return True
    except Exception as e:
        print(f"❌ [邮件告警] 发送失败: {e}")
        return False

def alert_action_failed(workflow_name, run_url):
    """GitHub Actions 失败时的邮件告警"""
    subject = f"🚨 GitHub Action 运行失败: {workflow_name}"
    content = f"您的 GitHub Action 工作流 '{workflow_name}' 运行失败。\n\n详情请查看: {run_url}"
    return send_email(subject, content)

class WebhookBackup:
    """Webhook 兜底逻辑：静默期 + 重试"""
    CACHE_FILE = ".webhook_cache.json"

    @staticmethod
    def get_cache():
        if os.path.exists(WebhookBackup.CACHE_FILE):
            try:
                with open(WebhookBackup.CACHE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"last_alert_time": 0, "retry_count": 0}

    @staticmethod
    def save_cache(cache):
        with open(WebhookBackup.CACHE_FILE, 'w') as f:
            json.dump(cache, f)

    @classmethod
    def trigger_backup_alert(cls, title, content):
        cache = cls.get_cache()
        now = time.time()
        
        # 30分钟静默期逻辑 (30 * 60 = 1800s)
        if now - cache["last_alert_time"] < 1800:
            print(f"⏳ [Webhook 兜底] 处于静默期，跳过邮件告警。上次告警时间: {time.ctime(cache['last_alert_time'])}")
            return

        # 重试逻辑
        success = False
        for i in range(3):
            print(f"🔄 [Webhook 兜底] 尝试发送邮件告警 (第 {i+1} 次)...")
            if send_email(f"Fallback: {title}", content):
                success = True
                break
            time.sleep(5) # 重试间隔

        if success:
            cache["last_alert_time"] = now
            cache["retry_count"] = 0
        else:
            cache["retry_count"] += 1
            print(f"❌ [Webhook 兜底] 邮件发送最终失败，当前累计失败次数: {cache['retry_count']}")
        
        cls.save_cache(cache)
