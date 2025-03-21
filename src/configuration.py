import logging
from pydantic import BaseModel, Field, ValidationError
from keboola.component.exceptions import UserException


class Configuration(BaseModel):
    gcp_service_account_key: str = Field(alias="#gcp_service_account_key")
    bucket_id: str
    report: str
    debug: bool = False

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise UserException(f"Validation Error: {', '.join(error_messages)}")

        if self.debug:
            logging.debug("Component will run in Debug mode")
