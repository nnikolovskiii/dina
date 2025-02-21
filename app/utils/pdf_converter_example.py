import json
from weasyprint import HTML
from jinja2 import Template

# Load JSON data (replace with your actual data)
data = {
    "ime": "",
    "prezime": "",
    "prezime_pred_brak": "",
    "den_mesec_godina_raganje": "",
    "mesto_raganje": "",
    "maticen_broj": "",
    "pol": "",
    "zivealiste_adresa": "",
    "drzavljanstvo": "",
    "tatko_ime": "",
    "majka_ime": "",
    "roditeli_1_ime": "",
    "roditeli_1_maticen_broj": "",
    "roditeli_1_srodstvo": "",
    "roditeli_1_potpis": "",
    "roditeli_2_ime": "",
    "roditeli_2_maticen_broj": "",
    "roditeli_2_srodstvo": "",
    "roditeli_2_potpis": "",
}

# HTML template for the simplified form
html_template = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: sans-serif; }
.container { width: 80%; margin: 20px auto; }
.section { margin-bottom: 20px; }
.label { font-weight: bold; }
.underline { text-decoration: underline; }
.checkbox { display: inline-block; margin-right: 5px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ddd; }
</style>
</head>
<body>
<div class="container">
    <h1>БАРАЊЕ ЗА ИЗДАВАЊЕ НА ЛИЧНА КАРТА</h1>

    <div class="section">
        <p><b>Причина за барање:</b></p>
        <p><span class="checkbox">☐</span> 1.1 прв пат  <span class="checkbox">☐</span> 1.2 редовна замена  <span class="checkbox">☐</span> 1.3 промена на податоци <span class="checkbox">☐</span> 1.4 дупликат  <span class="checkbox">☐</span> 1.5 оштетеност <span class="checkbox">☐</span> 1.6 ограничена важност</p>
    </div>

    <div class="section">
        <table>
            <tr>
                <td><b>1. ИМЕ</b><br>{{ data.ime }}</td>
                <td><b>2. ПРЕЗИМЕ</b><br>{{ data.prezime }}</td>
            </tr>
            <tr>
                <td colspan="2"><b>ЗА ОМАЖЕНИ-ОЖЕНЕТИ (презиме пред склучување на бракот)</b><br>{{ data.prezime_pred_brak }}</td>
            </tr>
            <tr>
                <td><b>ДЕН, МЕСЕЦ И ГОДИНА НА РАЃАЊЕ</b><br>{{ data.den_mesec_godina_raganje }}</td>
                <td><b>МЕСТО НА РАЃАЊЕ</b><br>{{ data.mesto_raganje }}</td>
            </tr>
            <tr>
                <td colspan="2"><b>МАТИЧЕН БРОЈ НА ГРАЃАНИНОТ</b><br>{{ data.maticen_broj }}</td>
            </tr>
            <tr>
                <td><b>ПОЛ</b><br>{{ data.pol }}</td>
                <td><b>ЖИВЕАЛИШТЕ И АДРЕСА</b><br>{{ data.zivealiste_adresa }}</td>
            </tr>
            <tr>
                <td colspan="2"><b>ДРЖАВЈАНСТВО</b><br>{{ data.drzavljanstvo }}</td>
            </tr>
            <tr>
                <td><b>Татко:</b><br>{{ data.tatko_ime }}</td>
                <td><b>Мајка:</b><br>{{ data.majka_ime }}</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <p><b>3. СОГЛАСНОСТ ОД РОДИТЕЛИТЕ-СТАРАТЕЛОТ</b></p>
        <table>
            <thead>
                <tr>
                    <th>Име и презиме</th>
                    <th>Матичен број</th>
                    <th>Сродство</th>
                    <th>Потпис</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{ data.roditeli_1_ime }}</td>
                    <td>{{ data.roditeli_1_maticen_broj }}</td>
                    <td>{{ data.roditeli_1_srodstvo }}</td>
                    <td>{{ data.roditeli_1_potpis }}</td>
                </tr>
                <tr>
                    <td>{{ data.roditeli_2_ime }}</td>
                    <td>{{ data.roditeli_2_maticen_broj }}</td>
                    <td>{{ data.roditeli_2_srodstvo }}</td>
                    <td>{{ data.roditeli_2_potpis }}</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="section">
        <h2>4. ПОДАТОЦИ ЗА ПРЕТХОДЕН ДОКУМЕНТ НА ПОДНОСИТЕЛОТ</h2>
        <p><span class="label">БРОЈ НА ЛИЧНА КАРТА:</span> <span class="underline">{{ data.licna_karta_broj }}</span></p>
        <p><span class="label">ОРГАН КОЈ ЈА ИЗДАЛ:</span> <span class="underline">{{ data.organ_izdal }}</span></p>
        <p>Потпис на подносителот _______________________________</p>
        <p>Датум и место на поднесување на барањето: _______________________________ 20____</p>
        <p>Податоци за контакт: _______________________________</p>
        <p>Потпис на службеното лице кое го примило барањето _______________________________</p>
    </div>

    <div class="section">
        <h2>5. ПРИЛОГ КОН БАРАЊЕТО:</h2>
        <ul>
            <li><span class="checkbox">&#x25A1;</span> При поднесување на барањето се врши проверка на идентитетот...</li>
            <li><span class="checkbox">&#x25A1;</span> Извод од матичната книга на родените...</li>
            <li><span class="checkbox">&#x25A1;</span> Доказ за промена на личните податоци...</li>
            <li><span class="checkbox">&#x25A1;</span> Доказ за промена на адреса...</li>
            <li><span class="checkbox">&#x25A1;</span> Доказ дека личната карта е огласена за неважечка...</li>
            <li><span class="checkbox">&#x25A1;</span> Пријава/изјава/потврда за изгубена или украдена лична карта...</li>
            <li><span class="checkbox">&#x25A1;</span> Други документи неопходни за постапката...</li>
        </ul>
        <p>Доказите означени со ѕвезда (*) се смета дека се поднесени... </p>
    </div>

    <div class="section">
        <h2>6. СОГЛАСНОСТ ОД ПОДНОСИТЕЛОТ НА БАРАЊЕТО</h2>
        <p>Подносителот на барањето е согласен неговите/нивните лични податоци да се користат...</p>
        <p>Потпис на подносителот _______________________________</p>
    </div>

    <div class="section">
        <h2>УПАТСТВО ЗА ПОПОЛНУВАЊЕ НА БАРАЊЕТО ЗА ИЗДАВАЊЕ ЛИЧНА КАРТА:</h2>
        <p>- Податоците од делот 1 и 2, ги пополнува подносителот на барањето;</p>
        <p>- Податоците од делот 3 ги пополнуваат родителите-старателите...</p>
        <p>- Податоците од делот 4 ги пополнува службеното лице;</p>
        <p>- Подносителот на барањето самиот го избира начинот на кој Министерството...</p>
        <p>- Доколку во текот на постапката се појави потреба од прибавување на документите...</p>
    </div>

</div>

</body>
</html>
"""

# Render HTML and generate PDF
template = Template(html_template)
html_content = template.render(data=data)
HTML(string=html_content).write_pdf('obrazec_licna_karta.pdf')
