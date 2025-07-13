from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route('/api/mandat', methods=['GET'])
def get_mandat():
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({'error': 'ID yuborilmadi'}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://mandat.uzbmb.uz/Mandat2024/")

            page.wait_for_selector('input[name="id"]')  # yoki to‘g‘ri selektor
            page.fill("input[name=id]", user_id)
            page.click("button[type=submit]")
            page.wait_for_timeout(3000)
            page.click("text=Batafsil")
            page.wait_for_timeout(2000)

            full_name = page.locator("text=F.I.SH").nth(0).evaluate("node => node.nextSibling.textContent").strip()
            score = page.locator("text=To‘plagan ball").nth(0).evaluate("node => node.nextSibling.textContent").strip()

            rows = page.locator("table tr").all()
            directions = []
            for row in rows[1:]:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
