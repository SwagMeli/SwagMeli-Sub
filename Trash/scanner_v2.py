import asyncio
import base64
import json
import re
import time
import urllib.request

# تنظیمات اصلی
INPUT_FILE = "Trash/Test.txt"
OUTPUT_FILE = "main/final.txt"
MY_TAG = "@SwagMeli"

def get_flag(country_code):
    """تبدیل کد کشور به ایموجی پرچم"""
    if not country_code or country_code == "UN": return "🌐"
    OFFSET = 127397
    return chr(ord(country_code[0].upper()) + OFFSET) + chr(ord(country_code[1].upper()) + OFFSET)

def get_geo(ip):
    """گرفتن اطلاعات کشور از API رایگان"""
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode"
        # رعایت محدودیت API (حداکثر 45 درخواست در دقیقه)
        time.sleep(1.2) 
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get('status') == 'success':
                return data.get('countryCode', 'UN'), data.get('country', 'Unknown')
    except:
        pass
    return "UN", "Unknown"

async def check_ping(host, port):
    """تست سریع زنده بودن سرور"""
    try:
        start_time = time.time()
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=3.0)
        ping = int((time.time() - start_time) * 1000)
        writer.close()
        await writer.wait_closed()
        return ping
    except:
        return None

async def process_configs():
    print("🚀 عملیات اسکن هوشمند شروع شد...")
    try:
        with open(INPUT_FILE, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ فایل ورودی یافت نشد!")
        return

    # پیدا کردن انواع لینک‌ها با Regex
    pattern = r'(vless|vmess|trojan|ss)://[^\s|#|\'|"]+'
    configs = re.findall(pattern, content)
    final_results = []

    for link in configs:
        # استخراج آدرس و پورت
        host_port = re.search(r'@([^:/]+):(\d+)', link)
        if not host_port: continue
        host, port = host_port.group(1), int(host_port.group(2))
        proto = link.split("://")[0]

        # تست پینگ
        ping = await check_ping(host, port)
        if ping:
            cc, country_name = get_geo(host)
            flag = get_flag(cc)
            new_name = f"{flag} {country_name} | {ping}ms | {MY_TAG}"
            
            # مدیریت پروتکل VMess (نیاز به دیکد/انکد JSON دارد)
            if proto == "vmess":
                try:
                    v_body = link.split("://")[1].split("#")[0]
                    v_body += "=" * ((4 - len(v_body) % 4) % 4) # رفع خطای Padding
                    v_data = json.loads(base64.b64decode(v_body).decode())
                    v_data['ps'] = new_name
                    new_link = "vmess://" + base64.b64encode(json.dumps(v_data).encode()).decode()
                except: continue
            # مدیریت VLESS, Trojan, SS (تغییر بخش بعد از #)
            else:
                clean_link = link.split("#")[0]
                new_link = f"{clean_link}#{new_name}"
            
            final_results.append(new_link)
            print(f"✅ تایید شد: {country_name} ({ping}ms)")

    # ذخیره نهایی
    if final_results:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(final_results))
        print(f"✨ پایان! {len(final_results)} کانفیگ سالم ذخیره شد.")

if __name__ == "__main__":
    asyncio.run(process_configs())
