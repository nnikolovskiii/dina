from datetime import datetime
from typing import Optional

from app.auth.models.user import GenderEnum
from app.chat_forms.templates.doc_template import UserDocument

from app.chat_forms.templates.driver_licnece import OtherLanguages
from app.databases.mongo_db import MongoEntry


class BirthCertificate(UserDocument):
    name: Optional[str] = None
    surname: Optional[str] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[datetime] = None
    birth_place: Optional[str] = None
    citizenship: Optional[str] = None
    # e_id is personal_id_number
    e_id: Optional[str] = None

    municipality: Optional[str] = None
    city: Optional[str] = None
    registration_place: Optional[str] = None
    current_number: Optional[str] = None
    registration_year: Optional[str] = None

    father_name: Optional[str] = None
    father_surname: Optional[str] = None
    father_personal_id: Optional[str] = None
    mother_name: Optional[str] = None
    mother_surname: Optional[str] = None
    mother_personal_id: Optional[str] = None
    parents_residence_address: Optional[str] = None

    # TODO: Implement this in later iteration
    # Document Metadata
    # notes: Optional[str] = None
    # document_number: Optional[str] = None  # Footer's Br.
    # issue_year: Optional[str] = None  # Footer's god.
    # registrar_signature: Optional[str] = None

    def get_template(self) -> str:
        return f"""<!DOCTYPE html>
    <html lang="mk">
    <head>
        <meta charset="UTF-8">
        <title>Матична книга</title>
        <style>
            @page {{
                size: A4;
                margin: 0;
            }}
            body {{
                font-family: 'Arial Unicode MS', sans-serif;
                margin: 0;
                padding: 1.6cm 2.0cm;
                font-size: 14px;
                position: relative;
                min-height: 29.7cm;
                width: 21cm;
            }}
            .header {{
                text-align: center;
                margin-bottom: 22px;
            }}
            .form-number {{
                font-size: 15px;
                margin-bottom: 10px;
            }}
            .underline {{
                border-bottom: 1px solid #000;
                display: inline-block;
                min-width: 250px;
                margin-left: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 6px 0;
            }}
            td {{
                border: 1px solid #000;
                padding: 6px 8px;
                height: 32px;
                vertical-align: top;
            }}
            .parent-table td {{
                width: 50%;
                height: 34px;
            }}
            .notes-box {{
                border: 1px solid #000;
                height: 98px;
                margin-top: 6px;
            }}
            .footer {{
                position: absolute;
                bottom: 1.8cm;
                right: 2.0cm;
                text-align: left;
            }}
            .signature-line {{
                width: 220px;
                border-top: 1px solid #000;
                margin-top: 22px;
            }}
        </style>
    </head>
    <body>
        <!-- Header Section -->
        <div class="header">
            <div class="form-number">Образец - 4-в</div>
            <h2 style="margin:4px 0;font-size:18px;">РЕПУБЛИКА СЕВЕРНА МАКЕДОНИЈА</h2>
            <h3 style="margin:8px 0;font-size:16px;">ИЗВОД ОД МАТИЧНАТА КНИГА НА РОДЕНИТЕ</h3>
        </div>

        <!-- Municipality/City -->
        <div style="margin-bottom:18px;">
            <div>ОПШТИНА <span class="underline">{self.municipality or ''}</span></div>
            <div style="margin-top:12px;">ГРАД <span class="underline">{self.city or ''}</span></div>
        </div>

        <!-- Main Content -->
        <div style="margin-bottom:16px;">
            Во матичната книга на родените што се води за местото <span class="underline">{self.registration_place or ''}</span><br>
            под тековен број <span class="underline" style="min-width:80px;">{self.current_number or ''}</span> за година <span class="underline" style="min-width:80px;">{self.registration_year or ''}</span> запишано е раганьето на:
        </div>

        <!-- Personal Data Table -->
        <table style="margin-bottom:10px;">
            <tr>
                <td style="width:68%; height:36px;">{self.name or ''}</td>
                <td style="width:32%;">{self.gender.value if self.gender else ''}</td>
            </tr>
            <tr>
                <td colspan="2" style="height:36px;">{self.surname or ''}</td>
            </tr>
        </table>

        <!-- Details Table -->
        <table style="margin-bottom:12px;">
            <tr><td style="height:36px;">{self.date_of_birth.strftime('%d.%m.%Y %H:%M') if self.date_of_birth else ''}</td></tr>
            <tr><td style="height:36px;">{self.birth_place or ''}</td></tr>
            <tr><td style="height:36px;">{self.citizenship or ''}</td></tr>
            <tr><td style="height:36px;">{self.e_id or ''}</td></tr>
        </table>

        <!-- Parents Table -->
        <div style="margin:8px 0 6px 0; font-weight:bold;">Податоци за родителите</div>
        <table class="parent-table">
            <tr>
                <td>Татко</td>
                <td>Мајка</td>
            </tr>
            <tr>
                <td>{self.father_first_name}</td>
                <td>{self.mother_first_name}</td>
            </tr>
            <tr>
                <td>{self.father_surname}</td>
                <td>{self.mother_surname}</td>
            </tr>
            <tr>
                <td>{self.father_personal_id}</td>
                <td>{self.mother_personal_id}</td>
            </tr>
            <tr>
                <td colspan="2" style="height:38px;">{self.parents_residence_address or ''}</td>
            </tr>
        </table>

        <!-- Notes Section -->
        <div style="margin-top:16px;">
            <strong>Забелешки:</strong>
            <div class="notes-box"></div>
        </div>
        <!-- Footer -->
        <div class="footer">
            <div>Бр. <span class="underline" style="min-width:100px;">{self.current_number or ''}</span></div>
            <div style="margin-top:10px;">год. <span class="underline" style="min-width:100px;">{self.registration_year or ''}</span></div>
            <div style="margin-top:24px;">Потпис на матичарог</div>
            <div class="signature-line"></div>
        </div>
    </body>
    </html>
            """
