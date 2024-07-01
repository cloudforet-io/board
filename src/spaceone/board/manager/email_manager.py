import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from spaceone.core import config
from spaceone.core.manager import BaseManager
from spaceone.board.connector.smtp_connector import SMTPConnector

_LOGGER = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), f"../template")
JINJA_ENV = Environment(
    loader=FileSystemLoader(searchpath=TEMPLATE_PATH), autoescape=select_autoescape()
)

LANGUAGE_MAPPER = {
    "default": {
        "reset_password": "Reset your password",
        "temp_password": "Your password has been changed",
        "verify_email": "Verify your notification email",
        "invite_external_user": "You've been invited to join.",
    },
    "ko": {
        "reset_password": "비밀번호 재설정 안내",
        "temp_password": "임시 비밀번호 발급 안내",
        "verify_email": "알림전용 이메일 계정 인증 안내",
        "invite_external_user": "계정 초대 안내.",
    },
    "en": {
        "reset_password": "Reset your password",
        "temp_password": "Your password has been changed",
        "verify_email": "Verify your notification email",
        "invite_external_user": "You've been invited to join.",
    },
    "ja": {
        "reset_password": "パスワードリセットのご案内",
        "temp_password": "仮パスワード発行のご案内",
        "verify_email": "通知メールアカウント認証のご案内",
        "invite_external_user": "参加するように招待されました",
    },
}


class EmailManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smtp_connector = SMTPConnector()

    def send_notification_email(
        self, email: str, language: str, post_contents: str, post_title: str
    ):
        service_name = self._get_service_name()
        template = JINJA_ENV.get_template(f"notice_email_{language}.html")
        email_contents = template.render(
            markdown=post_contents,
            service_name=service_name,
            notice_title=post_title,
        )
        subject = f"[{service_name}] {post_title}"

        self.smtp_connector.send_email(email, subject, email_contents)
