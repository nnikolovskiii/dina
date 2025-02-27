from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from app.auth.models.user import GenderEnum
from app.databases.mongo_db import MongoEntry


class PersonalID(MongoEntry):
    email: EmailStr
    download_link: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    surname_before_marriage: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    place_of_birth: Optional[str] = None
    eid: Optional[str] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None
    nationality: Optional[str] = None
    mother_name: Optional[str] = None
    father_name: Optional[str] = None
    mother_eid: Optional[str] = None
    father_eid: Optional[str] = None
    personal_id: Optional[str] = None
    institution: Optional[str] = None


def get_personal_id_template(personal_id: PersonalID) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<style>
body {{ font-family: sans-serif; }}
.container {{ width: 80%; margin: 20px auto; }}
.section {{ margin-bottom: 20px; }}
.label {{ font-weight: bold; }}
.underline {{ text-decoration: underline; }}
.checkbox {{ display: inline-block; margin-right: 5px; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 8px; border: 1px solid #ddd; }}
</style>
</head>
<body>
<div class="container">
    <h1>БАРАЊЕ ЗА ИЗДАВАЊЕ НА ЛИЧНА КАРТА</h1>

    <div class="section">
        <p><b>Причина за барање:</b></p>
        <p><span class="checkbox">☐</span> 1.1 прв пат  <span class="checkbox">☐</span> 1.2 редовна замена  
           <span class="checkbox">☐</span> 1.3 промена на податоци <span class="checkbox">☐</span> 1.4 дупликат  
           <span class="checkbox">☐</span> 1.5 оштетеност <span class="checkbox">☐</span> 1.6 ограничена важност</p>
    </div>

    <div class="section">
        <table>
            <tr>
                <td><b>1. ИМЕ</b><br>{personal_id.name}</td>
                <td><b>2. ПРЕЗИМЕ</b><br>{personal_id.surname}</td>
            </tr>
            <tr>
                <td colspan="2"><b>ЗА ОМАЖЕНИ-ОЖЕНЕТИ (презиме пред склучување на бракот)</b><br>{personal_id.surname_before_marriage}</td>
            </tr>
            <tr>
                <td><b>ДЕН, МЕСЕЦ И ГОДИНА НА РАЃАЊЕ</b><br>{personal_id.date_of_birth.strftime("%d-%m-%Y")}</td>
                <td><b>МЕСТО НА РАЃАЊЕ</b><br>{personal_id.place_of_birth}</td>
            </tr>
            <tr>
                <td colspan="2"><b>МАТИЧЕН БРОЈ НА ГРАЃАНИНОТ</b><br>{personal_id.eid}</td>
            </tr>
            <tr>
                <td><b>ПОЛ</b><br>{personal_id.gender}</td>
                <td><b>ЖИВЕАЛИШТЕ И АДРЕСА</b><br>{personal_id.address}</td>
            </tr>
            <tr>
                <td colspan="2"><b>ДРЖАВЈАНСТВО</b><br>{personal_id.nationality}</td>
            </tr>
            <tr>
                <td><b>Татко:</b><br>{personal_id.father_name}</td>
                <td><b>Мајка:</b><br>{personal_id.mother_name}</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>4. ПОДАТОЦИ ЗА ПРЕТХОДЕН ДОКУМЕНТ НА ПОДНОСИТЕЛОТ</h2>
        <p><span class="label">БРОЈ НА ЛИЧНА КАРТА:</span> <span class="underline">{personal_id.personal_id}</span></p>
        <p><span class="label">ОРГАН КОЈ ЈА ИЗДАЛ:</span> <span class="underline">{personal_id.institution}</span></p>
        <p>Потпис на подносителот _______________________________</p>
        <p>Датум и место на поднесување на барањето: _______________________________ 20____</p>
        <p>Податоци за контакт: _______________________________</p>
        <p>Потпис на службеното лице кое го примило барањето _______________________________</p>
    </div>

</div>

</body>
</html>
"""
