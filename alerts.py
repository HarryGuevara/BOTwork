import os, smtplib, requests
from email.mime.text import MIMEText

def fmt_jobs_md(jobs):
    lines = []
    for j in jobs:
        line = f"- **{j.get('title')}** · {j.get('company')} · {j.get('location','')} · {j.get('workload','')} · [Aplicar]({j.get('apply_url')})"
        lines.append(line)
    return "\n".join(lines)

def send_email(cfg, subject, body):
    host = cfg.get("smtp_host")
    port = cfg.get("smtp_port", 587)
    user = os.environ.get("SMTP_USERNAME", cfg.get("username"))
    pwd  = os.environ.get("SMTP_PASSWORD", cfg.get("password"))
    to   = cfg.get("to")
    if not (host and user and pwd and to):
        print("⚠️ Email no configurado/credenciales faltantes")
        return
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    with smtplib.SMTP(host, port) as s:
        s.starttls()
        s.login(user, pwd)
        s.sendmail(user, [to], msg.as_string())

def send_telegram(cfg, text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", cfg.get("bot_token"))
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", cfg.get("chat_id"))
    if not (token and chat_id):
        print("⚠️ Telegram no configurado")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})
    if resp.status_code != 200:
        print("⚠️ Telegram error:", resp.text)

def maybe_notify(config, new_jobs):
    notif = config.get("notifications", {})
    if not new_jobs:
        return
    subject = f"JobBot: {len(new_jobs)} oferta(s) nueva(s)"
    text = fmt_jobs_md(new_jobs)
    email_cfg = notif.get("email", {})
    if email_cfg.get("enabled"):
        send_email(email_cfg, subject, text)
    tg_cfg = notif.get("telegram", {})
    if tg_cfg.get("enabled"):
        send_telegram(tg_cfg, f"{subject}\n\n{text}")
