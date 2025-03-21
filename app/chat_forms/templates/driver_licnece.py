from datetime import datetime
from typing import Optional, List

import enum

from app.chat_forms.templates.doc_template import UserDocument


class SubmissionReason(str, enum.Enum):
    ISSUANCE_FIRST_TIME = "issuance_first_time"
    REPLACEMENT_FOREIGN_LICENSE = "replacement_foreign_license"
    REPLACEMENT_EXPIRATION = "replacement_expiration"
    REPLACEMENT_LOST_DAMAGED = "replacement_lost_damaged"
    REPLACEMENT_PERSONAL_DATA_CHANGE = "replacement_personal_data_change"
    REPLACEMENT_NEW_CATEGORY = "replacement_new_category"
    REPLACEMENT_CHANGE_RESIDENCE = "replacement_change_residence"
    ISSUANCE_DUPLICATE = "issuance_duplicate"
    REPLACEMENT_HEALTH_RESTRICTIONS = "replacement_health_restrictions"
    EXTENSION_VALIDITY_RESIDENCE = "extension_validity_residence"


class OtherLanguages(str, enum.Enum):
    TURKISH = "turkish"
    VLASKI = "vlaški"
    SERBIAN = "serbian"
    ROMANI = "romani"
    BOSNIAN = "bosnian"


class IssuanceProcedure(str, enum.Enum):
    REGULAR = "regular"
    URGENT = "urgent"


# TODO: There are other missing information!!!
class DriverLicence(UserDocument):
    reason_for_submission: Optional[List[SubmissionReason]] = None
    # name: Optional[str] = None
    # surname: Optional[str] = None
    other_languages: Optional[List[OtherLanguages]] = None
    e_id: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    issuance_procedure: Optional[IssuanceProcedure] = None
    municipality: Optional[str] = None
    settlement: Optional[str] = None
    living_address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    previous_licence_number: Optional[str] = None
    previous_issuing_authority: Optional[str] = None

    def get_template(self) -> str:
        return f"""<!DOCTYPE html>
<html lang="mk">
<head>
    <meta charset="UTF-8">
    <title>Барање за издавање на возачка дозвола</title>
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
        <div class="section" style="text-align: center;">
            <h3>Образец бр. 1</h3>
            <p>ДО: МИНИСТЕРСТВО ЗА ВНАТРЕШНИ РАБОТИ</p>
            <h2>БАРАЊЕ ЗА ИЗДАВАЊЕ НА ВОЗАЧКА ДОЗВОЛА</h2>
        </div>

        <div class="section">
            <h4>Причина за барање (се одбира еден од основните):</h4>
            <div>
                <span class="checkbox"></span> 1.1 прв пат<br>
                <span class="checkbox"></span> 1.2 редовна замена<br>
                <span class="checkbox"></span> 1.3 промена на податоци<br>
                <span class="checkbox"></span> 1.4 дупликат возачка дозвола<br>
                <span class="checkbox"></span> 1.5 предвремена замена<br>
                <span class="checkbox"></span> 1.6 дозвола со ограничена важност
            </div>
        </div>

        <div class="section">
            <h4>2. ПОДАТОЦИ ЗА ПОДНОСИТЕЛОТ НА БАРАЊЕТО</h4>
            <table>
                <tr>
                    <th>Матичен број</th>
                    <th>Датум на раѓање</th>
                </tr>
                <tr>
                    <td><div >{self.e_id}</div></td>
                    <td><div >{self.date_of_birth.strftime("%d-%m-%Y")}</div></td>
                </tr>
            </table>

            <h4>Постапка за издавање:</h4>
            <div>
                <span class="checkbox"></span> {self.issuance_procedure}
            </div>

            <h4>Други податоци:</h4>
            <table>
                <tr><td>Општина: <div  style="width:200px">{self.municipality}</div></td></tr>
                <tr><td>Населено место: <div  style="width:200px">{self.settlement}</div></td></tr>
                <tr><td>Адреса: <div >{self.living_address}</div></td></tr>
                <tr><td>Телефон: <div >{self.phone}</div></td></tr>
                <tr><td>Е-пошта: <div >{self.email}</div></td></tr>
            </table>
        </div>

        <div class="section official-use">
            <h4>3. ПОДАТОЦИ ЗА ПРЕТХОДНА ДОЗВОЛА</h4>
            <p>Број на претходна дозвола: {self.previous_licence_number}</p>
            <p>Орган кој ја издал: {self.previous_issuing_authority}</p>
            
            <h4>Потпис на подносител:</h4>
            <div style="height: 50px; border: 1px solid black;"></div>
            
        </div>

        <div class="section">
            <h4>4. ПРИЛОГ КОН БАРАЊЕТО:</h4>
            <div style="margin-left: 20px;">
                <p><span class="checkbox"></span> Доказ за положен возачки испит</p>
                <p><span class="checkbox"></span> Лекарско уверение</p>
                <p><span class="checkbox"></span> Пријава за изгубена дозвола</p>
                <p><span class="checkbox"></span> Други документи</p>
            </div>
        </div>

        <div class="section">
            <h4>5. СОГЛАСНОСТ НА ПОДНОСИТЕЛОТ</h4>
            <p>Подносителот ги потврдува сите податоци и се согласува со обработката на личните податоци.</p>
            <div style="height: 30px; border-bottom: 1px solid black; width: 300px;"></div>
            <p>(Потпис на подносител)</p>
        </div>
    </div>
</body>
</html>"""
