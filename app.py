from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

@app.route('/api/mandat')
def get_mandat():
    user_id = request.args.get('id')
    if not user_id:
        print("🚫 ID kiritilmagan")
        return jsonify({'error': 'ID yuborilmadi'}), 400

    try:
        print(f"🟢 ID qabul qilindi: {user_id}")

        with sync_playwright() as p:
            print("🧠 Playwright ishga tushdi")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            print("🔄 Saytga kirilmoqda...")
            page.goto("https://mandat.uzbmb.uz/", timeout=60000)

            print("⌛ ID inputni kutyapti...")
            page.wait_for_selector('input[placeholder="ID kiriting"]', timeout=60000)
            page.fill('input[placeholder="ID kiriting"]', user_id)
            print("✅ ID yozildi")

            page.click("button[type='submit']")
            print("🔍 Qidirish bosildi")
            page.wait_for_timeout(3000)

            print("📄 Batafsil tugmasini kutyapti...")
            page.wait_for_selector("a.btn.btn-info", timeout=10000)
            page.click("a.btn.btn-info")
            print("✅ Batafsil bosildi")
            page.wait_for_timeout(3000)

            print("📤 Ma'lumotlarni olish...")
            full_name = page.locator("strong:has-text('F.I.SH')").nth(0).evaluate(
                "e => e.parentElement.textContent.split(':')[1].trim()")
            score = page.locator("strong:has-text('To‘plagan ball')").nth(0).evaluate(
                "e => e.parentElement.textContent.split(':')[1].trim()")

            directions = []
            rows = page.locator("table tbody tr").all()
            for row in rows:
                cells = row.locator("td").all()
                if len(cells) >= 6:
                    directions.append({
                        "OTM": cells[0].inner_text().strip(),
                        "Yo‘nalish": cells[1].inner_text().strip(),
                        "Ta'lim shakli": cells[2].inner_text().strip(),
                        "Shifr": cells[3].inner_text().strip(),
                        "Grant": cells[4].inner_text().strip(),
                        "Kontrakt": cells[5].inner_text().strip(),
                    })

            browser.close()

            print("✅ Ma'lumotlar tayyor")
            return jsonify({
                "id": user_id,
                "full_name": full_name,
                "ball": score,
                "directions": directions
            })

    except Exception as e:
        print("❌ XATO:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 API {port}-portda ishga tushdi")
    app.run(host='0.0.0.0', port=port)
