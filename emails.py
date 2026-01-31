import smtplib
import ssl
from email.message import EmailMessage
from typing import List, Optional, Union
import mimetypes
import os
from dotenv import load_dotenv

# Explicitly load .env from the current directory
load_dotenv()


class EmailSender:
    def __init__(
            self,
            smtp_server: str,
            port: int,
            username: str,
            password: str,
            use_tls: bool = True,
    ):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send_email(
            self,
            subject: str,
            body: str,
            to_emails: Union[List[str], str],  # Fixed type hinting for older Python versions
            from_email: Optional[str] = None,
            html: bool = False,
            attachments: Optional[List[str]] = None,
    ) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email or self.username
        msg["To"] = ", ".join(to_emails) if isinstance(to_emails, list) else to_emails

        # Use add_alternative for HTML to ensure plain-text fallback
        if html:
            msg.set_content("Please use an HTML-compatible email client.")
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        if attachments:
            for file_path in attachments:
                if not os.path.isfile(file_path):
                    raise FileNotFoundError(f"Attachment not found: {file_path}")

                mime_type, _ = mimetypes.guess_type(file_path)
                maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)

                with open(file_path, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(file_path)
                    )

        context = ssl.create_default_context()

        # Port 587 uses starttls; Port 465 uses SMTP_SSL
        if self.use_tls:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.ehlo()  # Identify yourself to the server
                server.starttls(context=context)
                server.ehlo()
                server.login(self.username, self.password)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                server.login(self.username, self.password)
                server.send_message(msg)


if __name__ == "__main__":
    # --- TROUBLESHOOTING CHECK ---
    user = os.getenv("CB_EMAIL")
    pwd = os.getenv("CB_EMAIL_PWD")

    if not user or not pwd:
        print("❌ Error: Environment variables CB_EMAIL or CB_EMAIL_PWD are not set.")
    else:
        email_sender = EmailSender(
            smtp_server="smtp.gmail.com",
            port=587,
            username=user,
            password=pwd,
            use_tls=True
        )

        try:
            email_sender.send_email(
                subject="Test Email",
                body="<h1>Success!</h1><p>This is a test email.</p>",
                to_emails="geethapriya.sj@GMAIL.COM",  # Update this!
                html=True
            )
            print("✅ Email sent successfully!")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")