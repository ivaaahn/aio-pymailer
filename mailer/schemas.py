from pydantic import BaseModel


class TemplateBody(BaseModel):
    title: str
    name: str


class MsgToSend(BaseModel):
    subject: str
    recipients: list[str]
    body: str | None = None
    template_body: TemplateBody | None = None
    subtype: str = "html"

    def __pretty_recipients(self) -> str:
        return ", ".join([r for r in self.recipients])

    def __str__(self) -> str:
        recipients = self.__pretty_recipients()
        subj = self.subject

        if self.template_body:
            body_title = self.template_body.title
            body_name = self.template_body.name
        else:
            body_title = ""
            body_name = ""

        return f"Recipients: {recipients}. Subject: {subj}, Title: {body_title}, Name: {body_name}"
