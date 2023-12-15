import re
import uuid
from typing import Union
from pydantic import BaseModel, validator


class Report(BaseModel):

    type: str
    uid: uuid.UUID
    path: str

    @validator('uid')
    def check_uid(cls, uid):
        if not isinstance(uid, uuid.UUID):
            try:
                uid = uuid.UUID(uid)
            except:
                raise ValueError('Invalid UUID')
        return uid
