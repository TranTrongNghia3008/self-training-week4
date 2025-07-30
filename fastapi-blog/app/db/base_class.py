from sqlalchemy.ext.declarative import as_declarative, declared_attr
from typing import Any

@as_declarative()
class Base:
    id: Any
    __name__: str

    # Auto-generate __tablename__
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()