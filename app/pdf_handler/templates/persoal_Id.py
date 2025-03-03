from datetime import datetime
from typing import Optional

from app.auth.models.user import GenderEnum
from app.pdf_handler.templates.doc_template import UserDocument


class PersonalID(UserDocument):
    name: Optional[str] = None
    surname: Optional[str] = None
    surname_before_marriage: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    place_of_birth: Optional[str] = None
    e_id: Optional[str] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None
    nationality: Optional[str] = None
    mother_name: Optional[str] = None
    father_name: Optional[str] = None
    mother_eid: Optional[str] = None
    father_eid: Optional[str] = None
    personal_id: Optional[str] = None
    institution: Optional[str] = None

    def get_template(self) -> str:
        return f"""<!DOCTYPE html>
        <html lang="mk">
        <head>
            <meta charset="UTF-8">
            <title>Барање за издавање на лична карта (Тип-А)</title>
            <style>
                body {{ font-family: "Times New Roman", serif; margin: 20px; }}
                .law-form {{ max-width: 800px; margin: auto; }}
                .section {{ margin-bottom: 25px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                td, th {{ border: 1px solid black; padding: 8px; vertical-align: top; }}
                .underline {{ border-bottom: 1px solid black; display: inline-block; min-width: 200px; }}
                .checkbox {{ width: 14px; height: 14px; border: 1px solid black; display: inline-block; margin-right: 5px; }}
                .official-use {{ background-color: #f0f0f0; padding: 5px; }}
            </style>
        </head>
        <body>
            <div class="law-form">
                <!-- Страница 1 -->
                <div class="section" style="text-align: center;">
                    <h3>Образец бр. 1</h3>
                    <p>ДО: МИНИСТЕРСТВО ЗА ВНАТРЕШНИ РАБОТИ</p>
                    <h2>БАРАЊЕ ЗА ИЗДАВАЊЕ НА ЛИЧНА КАРТА</h2>
                    <h3>ТИП-А</h3>
                </div>

                <!-- Секција 1 -->
                <div class="section">
                    <h4>Причина за барање (се одбира еден од основните):</h4>
                    <div>
                        <span class="checkbox"></span> 1.1 прв пат<br>
                        <span class="checkbox"></span> 1.2 редовна замена<br>
                        <span class="checkbox"></span> 1.3 промена на податоци<br>
                        <span class="checkbox"></span> 1.4 дупликат лична карта<br>
                        <span class="checkbox"></span> 1.5 предвремена замена<br>
                        <span class="checkbox"></span> 1.6 карта со ограничена важност
                    </div>
                </div>

                <!-- Секција 2 -->
                <div class="section">
                    <h4>2. ПОДАТОЦИ ЗА ПОДНОСИТЕЛОТ НА БАРАЊЕТО</h4>
                    <table>
                        <tr>
                            <th>1. ИМЕ<br><small>македонски јазик</small></th>
                            <th>2. ПРЕЗИМЕ<br><small>македонски јазик</small></th>
                        </tr>
                        <tr>
                            <td><div >{self.name}</div></td>
                            <td><div >{self.surname}</div></td>
                        </tr>
                    </table>

                    <h4>Јазик на карта:</h4>
                    <div>
                        <span class="checkbox"></span> 1. турски
                        <span class="checkbox"></span> 2. влашки
                        <span class="checkbox"></span> 3. српски<br>
                        <span class="checkbox"></span> 4. ромски
                        <span class="checkbox"></span> 5. босански
                    </div>

                    <h4>Други податоци:</h4>
                    <table>
                        <tr><td>Датум на раѓање: <div  style="width:120px">{self.date_of_birth.strftime("%d-%m-%Y")}</div></td></tr>
                        <tr><td>Место на раѓање: <div  style="width:300px">{self.place_of_birth}</div></td></tr>
                        <tr><td>Матичен број: <div  style="width:200px">{self.e_id}</div></td></tr>
                        <tr><td>Пол: <span class="checkbox"></span> машки <span class="checkbox"></span> женски</td></tr>
                        <tr><td>Живеалиште и адреса: <div >{self.address}</div></td></tr>
                        <tr><td>Државјанство: <div  style="width:200px">{self.nationality}</div></td></tr>
                    </table>
                </div>

                <!-- Секција 3 -->
                <div class="section">
                    <h4>3. СОГЛАСНОСТ ОД РОДИТЕЛИТЕ/СТАРАТЕЛОТ</h4>
                    <table>
                        <tr>
                            <th>Име и презиме</th>
                            <th>Матичен број</th>
                            <th>Сродство</th>
                            <th>Потпис</th>
                        </tr>
                        <tr><td><br><br>{self.father_name}</td><td>{self.father_eid}</td><td>Татко</td><td></td></tr>
                        <tr><td><br><br>{self.mother_name}</td><td>{self.mother_eid}</td><td>Мајка</td><td></td></tr>
                    </table>
                </div>

            <!-- Страница 2 -->
                <div class="section official-use">
                    <h4>4. ПОДАТОЦИ ЗА ПРЕТХОДЕН ДОКУМЕНТ</h4>
                    <p>Број на лична карта: {self.id}</p>
                    <p>Орган кој ја издал: {self.institution}</p>

                    <h4>Потпис на подносител:</h4>
                    <div style="height: 50px; border: 1px solid black;"></div>

                    <h4>Податоци за контакт:</h4>
                    <p>Телефон: </p>
                    <p>Е-пошта: {self.email}</p>
                </div>

                <!-- Секција 5 -->
                <div class="section">
                    <h4>5. ПРИЛОГ КОН БАРАЊЕТО:</h4>
                    <div style="margin-left: 20px;">
                        <p><span class="checkbox"></span> Извод од матична книга</p>
                        <p><span class="checkbox"></span> Доказ за промена на податоци</p>
                        <p><span class="checkbox"></span> Пријава за изгубена карта</p>
                        <p><span class="checkbox"></span> Други документи</p>
                    </div>
                </div>

                <!-- Секција 6 -->
                <div class="section">
                    <h4>6. СОГЛАСНОСТ НА ПОДНОСИТЕЛОТ</h4>
                    <p>Подносителот ги потврдува сите податоци и се согласува со обработката на личните податоци.</p>
                    <div style="height: 30px; border-bottom: 1px solid black; width: 300px;"></div>
                    <p>(Потпис на подносител)</p>
                </div>
            </div>
        </body>
        </html>
        """
