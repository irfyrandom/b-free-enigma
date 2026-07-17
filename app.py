from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import json
import os
import requests
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = 'my-secret-key-2024'

# فایل‌های تنظیمات (توی ریشه ساخته میشن)
CONFIG_FILE = 'bot_config.json'
LOG_FILE = 'bot_logs.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            'bot_token': '',
            'chat_id': '',
            'custom_message': '✅ سرور با موفقیت روشن شد!',
            'is_running': False
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        return default_config
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_logs():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_logs(logs):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def send_telegram_message(token, chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {'ok': False, 'error': str(e)}

# ==================== HTML پنل ====================

PANEL_HTML = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 پنل مدیریت ربات تلگرام</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Tahoma', sans-serif;
            background: #1a1a2e;
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #e94560;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }
        .card {
            background: #16213e;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid #0f3460;
        }
        .card h2 {
            color: #e94560;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            color: #aaa;
            font-size: 0.9em;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 10px;
            background: #0f3460;
            border: none;
            border-radius: 6px;
            color: #fff;
            font-size: 1em;
            box-sizing: border-box;
        }
        .form-group textarea {
            min-height: 80px;
            resize: vertical;
        }
        .form-group small {
            color: #888;
            display: block;
            margin-top: 4px;
        }
        .btn {
            background: #e94560;
            color: #fff;
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.3s;
            width: 100%;
        }
        .btn:hover {
            background: #c73652;
        }
        .btn-success {
            background: #27ae60;
        }
        .btn-success:hover {
            background: #2ecc71;
        }
        .btn-danger {
            background: #c0392b;
        }
        .btn-danger:hover {
            background: #e74c3c;
        }
        .status-box {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            background: #0f3460;
            border-radius: 8px;
            margin-top: 10px;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }
        .status-dot.online {
            background: #2ecc71;
        }
        .status-dot.offline {
            background: #e74c3c;
        }
        .status-text {
            color: #ccc;
        }
        .log-item {
            background: #0f3460;
            padding: 10px 15px;
            border-radius: 6px;
            margin-bottom: 8px;
            border-right: 3px solid #e94560;
        }
        .log-item .log-time {
            color: #888;
            font-size: 0.85em;
        }
        .log-item .log-msg {
            color: #ccc;
            margin-top: 3px;
        }
        .log-item .log-status {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-top: 3px;
        }
        .log-status.success {
            background: #27ae60;
            color: #fff;
        }
        .log-status.error {
            background: #c0392b;
            color: #fff;
        }
        .log-status.info {
            background: #2980b9;
            color: #fff;
        }
        .empty-msg {
            text-align: center;
            color: #888;
            padding: 30px;
        }
        .back-link {
            display: inline-block;
            color: #e94560;
            text-decoration: none;
            margin-bottom: 20px;
        }
        .back-link:hover {
            color: #c73652;
        }
        .row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        @media (max-width: 600px) {
            .row {
                grid-template-columns: 1fr;
            }
        }
        .test-result {
            margin-top: 10px;
            padding: 10px;
            border-radius: 6px;
            display: none;
        }
        .test-result.success {
            display: block;
            background: #27ae60;
            color: #fff;
        }
        .test-result.error {
            display: block;
            background: #c0392b;
            color: #fff;
        }
        .inline-buttons {
            display: flex;
            gap: 10px;
        }
        .inline-buttons .btn {
            flex: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← بازگشت به صفحه اصلی</a>
        <h1>🤖 پنل مدیریت ربات تلگرام</h1>
        <p class="subtitle">تنظیمات و مدیریت ربات</p>
        
        <!-- وضعیت -->
        <div class="card">
            <h2>📊 وضعیت ربات</h2>
            <div class="status-box">
                {% if config.is_running %}
                <span class="status-dot online"></span>
                <span class="status-text">✅ ربات فعال است</span>
                {% else %}
                <span class="status-dot offline"></span>
                <span class="status-text">❌ ربات غیرفعال است</span>
                {% endif %}
            </div>
            <div style="margin-top: 10px; color: #888; font-size: 0.9em;">
                توکن: {% if config.bot_token %}{{ config.bot_token[:10] }}...{% else %}تنظیم نشده{% endif %}
                <br>
                چت آیدی: {% if config.chat_id %}{{ config.chat_id }}{% else %}تنظیم نشده{% endif %}
            </div>
        </div>
        
        <!-- تنظیمات -->
        <div class="card">
            <h2>⚙️ تنظیمات ربات</h2>
            <form method="POST" action="/panel-all/save">
                <div class="form-group">
                    <label>توکن ربات تلگرام *</label>
                    <input type="text" name="bot_token" placeholder="مثلاً: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz" value="{{ config.bot_token }}" required>
                    <small>توکن را از @BotFather دریافت کن</small>
                </div>
                <div class="form-group">
                    <label>چت آیدی (Chat ID) *</label>
                    <input type="text" name="chat_id" placeholder="مثلاً: 123456789" value="{{ config.chat_id }}" required>
                    <small>برای دریافت چت آیدی به @userinfobot پیام بده</small>
                </div>
                <div class="form-group">
                    <label>پیام روشن شدن سرور</label>
                    <textarea name="custom_message" placeholder="پیامی که موقع روشن شدن سرور فرستاده میشه...">{{ config.custom_message }}</textarea>
                    <small>از HTML برای فرمت‌دهی استفاده کن (مثلاً &lt;b&gt;متن&lt;/b&gt;)</small>
                </div>
                <button type="submit" class="btn">💾 ذخیره تنظیمات</button>
            </form>
        </div>
        
        <!-- عملیات -->
        <div class="card">
            <h2>🎮 عملیات</h2>
            <div class="row">
                <form method="POST" action="/panel-all/test">
                    <button type="submit" class="btn btn-success">📤 ارسال پیام تست</button>
                </form>
                <form method="POST" action="/panel-all/start">
                    <button type="submit" class="btn">▶️ راه‌اندازی ربات</button>
                </form>
            </div>
            <div style="margin-top: 10px;">
                <form method="POST" action="/panel-all/stop">
                    <button type="submit" class="btn btn-danger">⏹️ توقف ربات</button>
                </form>
            </div>
            {% if test_result %}
            <div class="test-result {{ test_result.class }}" style="display:block;">
                {{ test_result.message }}
            </div>
            {% endif %}
        </div>
        
        <!-- لاگ‌ها -->
        <div class="card">
            <h2>📋 لاگ‌های ارسال</h2>
            {% if logs %}
                {% for log in logs|reverse %}
                <div class="log-item">
                    <div class="log-time">📅 {{ log.time }}</div>
                    <div class="log-msg">{{ log.message }}</div>
                    <span class="log-status {{ log.status }}">{{ log.status }}</span>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-msg">😅 هنوز لاگی ثبت نشده</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

# ==================== مسیرها ====================

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>ربات تلگرام</title></head>
    <body style="font-family:Tahoma;background:#1a1a2e;color:#fff;text-align:center;padding:50px;">
        <h1 style="color:#e94560;">🤖 ربات تلگرام</h1>
        <p>به پنل مدیریت ربات خوش آمدید</p>
        <br>
        <a href="/panel-all" style="background:#e94560;color:#fff;padding:12px 30px;border-radius:8px;text-decoration:none;">📊 ورود به پنل</a>
    </body>
    </html>
    '''

@app.route('/panel-all')
def panel():
    config = load_config()
    logs = load_logs()
    return render_template_string(PANEL_HTML, config=config, logs=logs, test_result=None)

@app.route('/panel-all/save', methods=['POST'])
def save_config_route():
    config = load_config()
    config['bot_token'] = request.form.get('bot_token', '').strip()
    config['chat_id'] = request.form.get('chat_id', '').strip()
    config['custom_message'] = request.form.get('custom_message', '✅ سرور با موفقیت روشن شد!').strip()
    
    if config['bot_token']:
        try:
            url = f"https://api.telegram.org/bot{config['bot_token']}/getMe"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                save_config(config)
                logs = load_logs()
                logs.append({
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': '✅ تنظیمات با موفقیت ذخیره شد',
                    'status': 'success'
                })
                save_logs(logs)
                return render_template_string(PANEL_HTML, config=config, logs=logs, test_result={
                    'class': 'success',
                    'message': '✅ تنظیمات ذخیره شد! توکن معتبر است.'
                })
        except:
            pass
    
    save_config(config)
    logs = load_logs()
    logs.append({
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': '⚠️ تنظیمات ذخیره شد اما توکن معتبر نیست!',
        'status': 'error'
    })
    save_logs(logs)
    
    return render_template_string(PANEL_HTML, config=config, logs=logs, test_result={
        'class': 'error',
        'message': '⚠️ تنظیمات ذخیره شد اما توکن معتبر نیست!'
    })

@app.route('/panel-all/test', methods=['POST'])
def test_message():
    config = load_config()
    logs = load_logs()
    
    if not config['bot_token'] or not config['chat_id']:
        return render_template_string(PANEL_HTML, config=config, logs=logs, test_result={
            'class': 'error',
            'message': '❌ لطفاً ابتدا توکن و چت آیدی را تنظیم کن!'
        })
    
    result = send_telegram_message(
        config['bot_token'],
        config['chat_id'],
        '🧪 <b>پیام تست</b>\n\nربات شما به درستی کار می‌کند!'
    )
    
    if result.get('ok'):
        logs.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': '📤 پیام تست با موفقیت ارسال شد',
            'status': 'success'
        })
        save_logs(logs)
        return render_template_string(PANEL_HTML, config=config, logs=logs, test_result={
            'class': 'success',
            'message': '✅ پیام تست با موفقیت ارسال شد!'
        })
    else:
        logs.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': f'❌ خطا در ارسال پیام تست: {result.get("error", "مشخص نیست")}',
            'status': 'error'
        })
        save_logs(logs)
        return render_template_string(PANEL_HTML, config=config, logs=logs, test_result={
            'class': 'error',
            'message': f'❌ خطا: {result.get("error", "مشخص نیست")}'
        })

@app.route('/panel-all/start', methods=['POST'])
def start_bot():
    config = load_config()
    logs = load_logs()
    
    if not config['bot_token'] or not config['chat_id']:
        return render_template_string(PANEL_HTML, config=config, logs=logs, test_result={
            'class': 'error',
            'message': '❌ لطفاً ابتدا توکن و چت آیدی را تنظیم کن!'
        })
    
    result = send_telegram_message(
        config['bot_token'],
        config['chat_id'],
        config['custom_message']
    )
    
    if result.get('ok'):
        config['is_running'] = True
        save_config(config)
        logs.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': '🚀 ربات راه‌اندازی شد و پیام روشن شدن ارسال گردید',
            'status': 'success'
        })
        save_logs(logs)
        return render_template_string(PANEL_HTML, config=config, logs=logs, test_result={
            'class': 'success',
            'message': '✅ ربات راه‌اندازی شد! پیام روشن شدن ارسال گردید.'
        })
    else:
        logs.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': f'❌ خطا در راه‌اندازی ربات: {result.get("error", "مشخص نیست")}',
            'status': 'error'
        })
        save_logs(logs)
        return render_template_string(PANEL_HTML, config=config, logs=logs, test_result={
            'class': 'error',
            'message': f'❌ خطا: {result.get("error", "مشخص نیست")}'
        })

@app.route('/panel-all/stop', methods=['POST'])
def stop_bot():
    config = load_config()
    logs = load_logs()
    
    config['is_running'] = False
    save_config(config)
    
    logs.append({
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': '⏹️ ربات متوقف شد',
        'status': 'info'
    })
    save_logs(logs)
    
    return render_template_string(PANEL_HTML, config=config, logs=logs, test_result={
        'class': 'success',
        'message': '✅ ربات با موفقیت متوقف شد!'
    })

# ==================== API برای Railway ====================

@app.route('/api/start_bot')
def api_start_bot():
    config = load_config()
    logs = load_logs()
    
    if not config['bot_token'] or not config['chat_id']:
        return jsonify({'status': 'error', 'message': 'تنظیمات کامل نیست!'})
    
    result = send_telegram_message(
        config['bot_token'],
        config['chat_id'],
        config['custom_message']
    )
    
    if result.get('ok'):
        config['is_running'] = True
        save_config(config)
        logs.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': '🚀 سرور روشن شد - پیام ارسال گردید',
            'status': 'success'
        })
        save_logs(logs)
        return jsonify({'status': 'success', 'message': 'پیام ارسال شد!'})
    else:
        logs.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': f'❌ خطا در ارسال پیام روشن شدن: {result.get("error", "مشخص نیست")}',
            'status': 'error'
        })
        save_logs(logs)
        return jsonify({'status': 'error', 'message': result.get('error', 'خطا')})

# ==================== اجرا ====================

if __name__ == '__main__':
    # ارسال پیام اولیه (اگه تنظیمات کامل باشه)
    time.sleep(2)
    config = load_config()
    if config['bot_token'] and config['chat_id']:
        try:
            result = send_telegram_message(
                config['bot_token'],
                config['chat_id'],
                '🚀 <b>سرور با موفقیت روشن شد!</b>\n\n' + config['custom_message']
            )
            if result.get('ok'):
                config['is_running'] = True
                save_config(config)
                logs = load_logs()
                logs.append({
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': '🚀 سرور روشن شد - پیام اولیه ارسال گردید',
                    'status': 'success'
                })
                save_logs(logs)
                print('✅ پیام اولیه ارسال شد!')
        except Exception as e:
            print(f'❌ خطا در ارسال پیام اولیه: {e}')
    
    # اجرا با پورت مناسب
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)