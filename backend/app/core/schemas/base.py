from pydantic import BaseModel, ConfigDict


class ORMReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
