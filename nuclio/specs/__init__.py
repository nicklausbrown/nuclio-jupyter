from pydantic import BaseModel


def to_camel(string: str) -> str:
    words = string.split('_')
    return words[0] + ''.join(word.capitalize() for word in words[1:])


class CamelBaseModel(BaseModel):
    class Config:
        alias_generator = to_camel
        validate_assignment = True
