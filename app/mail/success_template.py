def get_success_template():
    return f"""
        <html>
            <body style="margin: 0; padding: 20px; background: #f3f4f6; font-family: Arial, sans-serif;">
                <!--[if mso]>
                <style>
                    .check-container {{
                        width: 48px !important;
                        height: 48px !important;
                        background: #e2feee !important;
                        mso-line-height-rule: exactly;
                    }}
                    .check-fallback {{
                        display: block !important;
                        font-size: 24px;
                        color: #0afa2a;
                        line-height: 48px;
                    }}
                </style>
                <![endif]-->

                <div style="max-width: 320px; margin: 0 auto; background: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    <div style="position: relative; padding: 20px;">
                        <!-- Checkmark Container -->
                        <div class="check-container" style="width: 48px; height: 48px; background: #e2feee; border-radius: 50%; margin: 0 auto 20px; text-align: center;">
                            <!--[if mso]>
                                <div class="check-fallback">✓</div>
                            <![endif]-->
                            <!--[if !mso]><!-- -->
                            <svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: block; margin: auto;">
                                <path d="M20 7L9 18L4 13" 
                                      stroke="#0afa2a" 
                                      stroke-width="2.5" 
                                      stroke-linecap="round" 
                                      stroke-linejoin="round"/>
                            </svg>
                            <!--<![endif]-->
                        </div>

                        <!-- Rest of the content remains the same -->
                        <div style="text-align: center;">
                            <h1 style="color: #066e29; font-size: 18px; margin: 0 0 12px 0;">Успешно закажување на термин!</h1>
                            <p style="color: #595b5f; font-size: 14px; line-height: 1.5; margin: 0 0 24px 0;">Вашиот термин е успешно закажан на 23.03.2024 во 14 часот.</p>
                        </div>

                        <div style="margin: 0 20px 20px;">
                            <a href="#" style="display: block; padding: 12px; background: #1aa06d; color: #ffffff; text-decoration: none; border-radius: 6px; margin-bottom: 12px; text-align: center; font-weight: bold;">Покажи термини</a>
                            <a href="#" style="display: block; padding: 12px; border: 1px solid #D1D5DB; color: #242525; text-decoration: none; border-radius: 6px; text-align: center; font-weight: bold;">Зборувај со Дина</a>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
