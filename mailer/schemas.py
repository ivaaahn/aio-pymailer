from typing import Optional

from pydantic import BaseModel


class FormattedBody(BaseModel):
    title: str
    data: str
    description: Optional[str]


class MsgToSend(BaseModel):
    subject: str
    recipients: list[str]
    regular_body: Optional[str] = None
    formatted_body: Optional[FormattedBody] = None
    subtype: str = "html"

    def __pretty_recipients(self) -> str:
        return ", ".join([r for r in self.recipients])

    def __str__(self) -> str:
        recipients = self.__pretty_recipients()
        subj = self.subject

        if self.formatted_body:
            body_title = self.formatted_body.title
            body_data = self.formatted_body.data
            body_description = self.formatted_body.description
        else:
            body_title = ""
            body_data = ""
            body_description = ""

        return f"Recipients: {recipients}. Subject: {subj}, Title: {body_title}, Data: {body_data}, Description: {body_description}"
