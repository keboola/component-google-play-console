import logging
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, computed_field
from keboola.component.exceptions import UserException


class LoadType(str, Enum):
    full_load = "full_load"
    incremental_load = "incremental_load"


class Destination(BaseModel):
    load_type: LoadType = Field(default=LoadType.incremental_load)

    @computed_field
    def incremental(self) -> bool:
        return self.load_type == LoadType.incremental_load


class Configuration(BaseModel):
    gcp_service_account_key: str = Field(alias="#gcp_service_account_key")
    bucket_id: str
    reports: list[str]
    date_from: str
    destination: Destination
    debug: bool = False

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise UserException(f"Validation Error: {', '.join(error_messages)}")

        if self.debug:
            logging.debug("Component will run in Debug mode")
