from datetime import datetime
from typing import Optional

from app.auth.models.user import GenderEnum
from app.dina.pdf_templates.doc_template import UserDocument

import enum

from app.dina.pdf_templates.driver_licnece import OtherLanguages


class SubmissionReason(str, enum.Enum):
    FIRST_TIME = "прв пат"
    REGULAR_REPLACEMENT = "редовна замена"
    PERSONAL_DATA_CHANGE = "промена на лични податоци"
    OTHER_REASONS = "замена поради други причини (исполнетост или друго)"
    DUPLICATE_LOST_STOLEN = "дупликат пасош (изгубен, исчезнат или украден)"
    EARLY_REPLACEMENT_DAMAGED = "предвремена замена поради оштетеност на пасошот"
    LIMITED_VALIDITY = "издавање на пасош со ограничен рок на важење"


# TODO: Passport form needs to have a signature image and photo image.

class Passport(UserDocument):
    name: Optional[str] = None
    surname: Optional[str] = None
    submission_reason: Optional[SubmissionReason] = None
    document_number: Optional[str] = None
    date_of_issue: Optional[str] = None
    date_of_expiry: Optional[str] = None
    place_of_birth: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[GenderEnum] = None
    e_id: Optional[str] = None
    issuing_authority: Optional[str] = None
    other_language: Optional[OtherLanguages] = None

    # image_base64: Optional[str] = None
    # signature_base64: Optional[str] = None

    def get_template(self) -> str:
        return f"""<!DOCTYPE html>
        <html lang="mk">
        <head>
            <meta charset="UTF-8">
            <title>Барање за издавање на пасош</title>
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
                    <h2>БАРАЊЕ ЗА ИЗДАВАЊЕ НА ПАСОШ</h2>
                </div>

                <div class="section">
                    <h4>Причина за барање (се одбира еден од основните):</h4>
                    <div>
                        <span class="checkbox"></span> {SubmissionReason.FIRST_TIME.value}<br>
                        <span class="checkbox"></span> {SubmissionReason.REGULAR_REPLACEMENT.value}<br>
                        <span class="checkbox"></span> {SubmissionReason.PERSONAL_DATA_CHANGE.value}<br>
                        <span class="checkbox"></span> {SubmissionReason.DUPLICATE_LOST_STOLEN.value}<br>
                        <span class="checkbox"></span> {SubmissionReason.EARLY_REPLACEMENT_DAMAGED.value}<br>
                        <span class="checkbox"></span> {SubmissionReason.LIMITED_VALIDITY.value}<br>
                        <span class="checkbox"></span> {SubmissionReason.OTHER_REASONS.value}
                    </div>
                </div>

                <div class="section">
                    <h4>2. ПОДАТОЦИ ЗА ПОДНОСИТЕЛОТ НА БАРАЊЕТО</h4>
                    <table>
                        <tr>
                            <th>1. ИМЕ<br><small>македонски јазик</small></th>
                            <th>2. ПРЕЗИМЕ<br><small>македонски јазик</small></th>
                        </tr>
                        <tr>
                            <td><div>{self.name}</div></td>
                            <td><div>{self.surname}</div></td>
                        </tr>
                    </table>

                    <h4>Јазик на карта:</h4>
                    <div>
                        <span class="checkbox"></span> {OtherLanguages.TURKISH.value}
                        <span class="checkbox"></span> {OtherLanguages.VLASKI.value}
                        <span class="checkbox"></span> {OtherLanguages.SERBIAN.value}<br>
                        <span class="checkbox"></span> {OtherLanguages.ROMANI.value}
                        <span class="checkbox"></span> {OtherLanguages.BOSNIAN.value}
                    </div>

                    <h4>Други податоци:</h4>
                    <table>
                        <tr><td>Датум на раѓање: <div style="width:120px">{self.date_of_birth if self.date_of_birth else ""}</div></td></tr>
                        <tr><td>Место на раѓање: <div style="width:300px">{self.place_of_birth}</div></td></tr>
                        <tr><td>Матичен број: <div style="width:200px">{self.e_id}</div></td></tr>
                        <tr><td>Пол: <span class="checkbox"></span> {GenderEnum.MALE.value} <span class="checkbox"></span> {GenderEnum.FEMALE.value}</td></tr>
                        <tr><td>Орган кој издал: <div style="width:200px">{self.issuing_authority}</div></td></tr>
                        <tr><td>Број на документ: <div style="width:200px">{self.document_number}</div></td></tr>
                        <tr><td>Датум на издавање: <div style="width:120px">{self.date_of_issue if self.date_of_issue else ""}</div></td></tr>
                        <tr><td>Датум на истекување: <div style="width:120px">{self.date_of_expiry if self.date_of_expiry else ""}</div></td></tr>

                    </table>
                </div>

            </div>
        </body>
        </html>
        """
