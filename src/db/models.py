from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()],
    ),
    "ix": "ix_%(table_name)s__%(all_column_names)s",
    "uq": "uq_%(table_name)s__%(all_column_names)s",
    "ck": "ck_%(table_name)s__%(constraint_name)s",
    "fk": "fk_%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


class OurUser(Base):
    __tablename__ = "our_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None]
    telegram_id: Mapped[str | None] = mapped_column(unique=True)


class BlackListChat(Base):
    __tablename__ = "blacklist_chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    chat_id: Mapped[int | None] = mapped_column(unique=True)
