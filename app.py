from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route('/api/mandat')
def get_mandat():
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({'error': 'ID yuborilmadi'}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # 1. Kirish
            page.goto("https://mandat.uzbmb.uz/Mandat2024/", timeout=60000)
            page.wait_for_selector('input#SearchId')  # TO‘G‘RI SELECTOR
            page.fill('input#SearchId', user_id)

            # 2. Qidirish tugmasi
            page.click("button.btn.btn-primary[type='submit']")
            page.wait_for_timeout(3000)

            # 3. "Batafsil" tugmasi
            page.click("a.btn.btn-info")  # bu linkdagi batafsil tugmasi
            page.wait_for_timeout(3000)

            # 4. Ma’lumotlarni ajratib olish
            full_name = page.locator("strong:has-text('F.I.SH')").nth(0).evaluate("e => e.parentElement.textContent.split(':')[1].trim()")
            score = page.locator("strong:has-text('To‘plagan ball')").nth(0).evaluate("e => e.parentElement.textContent.split(':')[1].trim()")

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

            return jsonify({
                "id": user_id,
                "full_name": full_name,
                "ball": score,
                "directions": directions
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

