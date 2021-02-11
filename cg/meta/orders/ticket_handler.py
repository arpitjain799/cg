import logging
import re
from typing import Optional

from cg.apps.orderform.schemas.orderform_schema import OrderformSchema
from cg.apps.osticket import OsTicket
from cg.store import Store, models

LOG = logging.getLogger(__name__)


class TicketHandler:
    """Handle tickets in the meta orders context"""

    NEW_LINE = "<br />"

    def __init__(self, osticket_api: OsTicket, status_db: Store):
        self.osticket: OsTicket = osticket_api
        self.status_db: Store = status_db

    @staticmethod
    def parse_ticket_number(name: str) -> Optional[int]:
        """Try to parse a ticket number from a string"""
        # detect manual ticket assignment
        ticket_match = re.fullmatch(r"#([0-9]{6})", name)
        if ticket_match:
            ticket_number = int(ticket_match.group(1))
            LOG.info("%s: detected ticket in order name", ticket_number)
            return ticket_number
        LOG.info("Could not detected ticket number in name %s", name)
        return None

    def create_new_ticket_message(self, order: OrderformSchema, ticket: dict, project: str) -> str:
        message = f"data:text/html;charset=utf-8,New incoming {project} samples: "

        for sample in order.samples:
            self.add_sample_name_to_message(message=message, sample_name=sample.name)
            self.add_sample_apptag_to_message(message=message, application=sample.application)
            self.add_sample_case_name_to_message(message=message, case_name=sample.family_name)
            self.add_existing_sample_info_to_message(
                message=message, customer_id=order.customer, internal_id=sample.internal_id
            )
            self.add_sample_priority_to_message(message=message, priority=sample.priority)
            self.add_sample_comment_to_message(message=message, comment=sample.comment)

        message += self.NEW_LINE
        message = self.add_comment_to_message(order, message)
        message = self._add_user_name_to_message(message, ticket)
        message = self._add_customer_to_message(order, message)

        return message

    def add_sample_name_to_message(self, message: str, sample_name: str) -> None:
        message += self.NEW_LINE + sample_name

    @staticmethod
    def add_sample_apptag_to_message(message: str, application: Optional[str]) -> None:
        if application:
            message += f", application: {application}"

    @staticmethod
    def add_sample_case_name_to_message(message: str, case_name: Optional[str]):
        if case_name:
            message += f", case: {case_name}"

    def add_existing_sample_info_to_message(
        self, message: str, customer_id: str, internal_id: Optional[str]
    ) -> None:
        if not internal_id:
            return
        existing_sample: models.Sample = self.status_db.sample(internal_id)
        sample_customer = ""
        if existing_sample.customer_id != customer_id:
            sample_customer = " from " + existing_sample.customer.internal_id

        message += f" (already existing sample{sample_customer})"

    @staticmethod
    def add_sample_priority_to_message(message: str, priority: Optional[str]) -> None:
        if priority:
            message += ", priority: " + priority

    @staticmethod
    def add_sample_comment_to_message(message: str, comment: Optional[str]) -> None:
        if comment:
            message += ", " + comment

    def add_comment_to_message(self, comment: Optional[str], message: str):
        if not comment:
            return message

        message += self.NEW_LINE + f"{comment}."
        return message

    def add_user_name_to_message(self, name: Optional[None], message: str):
        if not name:
            return message

        message += self.NEW_LINE + f"{name}"
        return message
