import asyncio
import base64
import json
import re
import time
import urllib.request

# تنظیمات دقیق بر اساس اسم‌های تو
INPUT_FILE = "Trash/Test.txt"
OUTPUT_FILE = "main/final.txt"
MY_TAG = "@SwagMeli"

def get_flag(country_code):
    if not country_code or len(country_code) != 2: return "🌐"
    OFFSET = 127397
    return chr(ord(country_code[0].upper()) + OFFSET) + chr(ord(country_code[1].upper()) + OFFSET)

def get_geo(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode"
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode())
            if data['status'] == 'success':
                return data['countryCode'], data['country']
    except: pass
    return "UN", "Unknown"

async def check_connection(host, port):
    start = time.time()
    try:
        # تست پورت با Timeout کوتاه برای سرعت بالا
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=2.5)
        latency = int((time.time() - start) * 1000)
        writer.close()
        await writer.wait_closed()
        return latency
    except:
        return None

async def main():
    print(f"🚀 در حال شروع اسکنر V2 در پوشه Trash...")
    try:
        with open(INPUT_FILE, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ فایل {INPUT_FILE} پیدا نشد! مطمئن شو که اسم پوشه و فایل دقیقاً درسته.")
        return

    # پیدا کردن لینک‌های v2ray
    pattern = r'(vless|vmess|trojan|ss)://[^\s|#|\'|"]+'
    configs = re.findall(pattern, content)
    
    final_configs = []
    print(f"🔎 تعداد {len(configs)} کانفیگ پیدا شد. در حال پردازش...")

    for config in configs:
        # استخراج Host و Port از لینک
        parts = re.search(r'@([^:/]+):(\d+)', config)
        if not parts: continue
        
        host = parts.group(1)
        port = int(parts.group(2))
        proto = config.split("://")[0]

        # تست زنده بودن
        ms = await check_connection(host, port)
        if ms is not None:
            cc, cn = get_geo(host)
            flag = get_flag(cc)
            new_name = f"{flag} {cn} | {ms}ms | {MY_TAG}"
            
            # بازسازی با نام جدید (دیکد و تغییر اسم)
            if proto == "vmess":
                try:
                    v_body = config.split("://")[1]
                    # اصلاح Padding برای جلوگیری از خطای Base64
                    v_body += "=" * ((4 - len(v_body) % 4) % 4)
                    v_data = json.loads(base64.b64decode(v_body).decode())
                    v_data['ps'] = new_name
                    new_link = "vmess://" + base64.b64encode(json.dumps(v_data).encode()).decode()
                except: continue
            else:
                clean_link = config.split("#")[0]
                new_link = f"{clean_link}#{new_name}"
            
            final_configs.append(new_link)
            print(f"✅ تایید شد: {cn} ({ms}ms)")

    # ذخیره در مقصد
    try:
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(final_configs))
        print(f"✨ پایان! {len(final_configs)} کانفیگ در {OUTPUT_FILE} ذخیره شد.")
    except Exception as e:
        print(f"❌ خطا در ذخیره فایل: {e}")

if __name__ == "__main__":
    asyncio.run(main())

