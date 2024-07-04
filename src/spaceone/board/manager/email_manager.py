import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from spaceone.core import config
from spaceone.core.manager import BaseManager
from spaceone.board.connector.smtp_connector import SMTPConnector

_LOGGER = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), f"../template")
JINJA_ENV = Environment(
    loader=FileSystemLoader(searchpath=TEMPLATE_PATH),
    autoescape=select_autoescape(enabled_extensions="html"),
)


class EmailManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smtp_connector = SMTPConnector()

    def send_notification_email(
        self, email: str, language: str, post_contents: str, post_title: str
    ):
        try:
            service_name = self._get_service_name()
            template = JINJA_ENV.get_template(f"notice_email_{language}.html")
            email_contents = template.render(
                markdown=post_contents,
                service_name=service_name,
                notice_title=post_title,
            )
            subject = f"[{service_name}] {post_title}"

            self.smtp_connector.send_email(email, subject, email_contents)
        except Exception as e:
            _LOGGER.error(
                f"[send_notification_email] failed to send email to {email} {e}",
                exc_info=True,
            )

    @staticmethod
    def _get_service_name():
        return config.get_global("EMAIL_SERVICE_NAME")
