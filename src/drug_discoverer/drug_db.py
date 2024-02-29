import os
from typing import List

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Synonyms(Base):
    __tablename__ = "synonyms"  # Assuming 'synonyms' is the table name in public schema
    __table_args__ = {"schema": "public"}  # Specify the schema explicitly

    syn_id = Column(Integer, primary_key=True)
    id = Column(Integer)
    name = Column(String)
    preferred_name = Column(SmallInteger)
    parent_id = Column(Integer)
    lname = Column(String)


class DrugDB:
    """DrugDB class to interact with the database. It uses SQLAlchemy to connect to the database and
    provides a method to get synonyms from the database.

    NOTE: We assume that the DB is already created and the table 'synonyms' exists in the public schema!
    """

    def __init__(self, db_uri: str):
        self.engine = create_engine(
            db_uri, echo=False
        )  # Set echo to True for debugging
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def get_all_names(self, only_lowercase: bool = True) -> List[str]:
        """Get all the drug names from the database.
        If `only_lowercase` is True, it returns all the drug names in lowercase.
        """
        query_result = self.session.query(Synonyms).all()
        if only_lowercase:
            return [str(row.lname) for row in query_result]
        return [str(row.name) for row in query_result]

    def get_all_preferred_names(self) -> List[str]:
        """Get all the preferred drug names from the database.
        It returns all the `name` column values where the `preferred_name` column value is 1.
        """
        query_result = (
            self.session.query(Synonyms).filter(Synonyms.preferred_name == 1).all()
        )
        return [str(row.name) for row in query_result]

    def get_preferred_name(self, name: str, is_lower: bool = True) -> str:
        """Get the preferred name of a drug from the database.
        It first searches the lname column and then saves the `id` value.
        If the returned row has a `preferred_name` value of 1, it means that it is the preferred name
        and we return the `name` column value. Otherwise, we use the `id` value to search for the row
        with the `preferred_name` value of 1 and return the `name` column value.

        If is_lower is True then we will use the `lname` column, otherwise we will use the `name` column.
        """
        if is_lower:
            column_name = Synonyms.lname
        else:
            column_name = Synonyms.name
        query_result = self.session.query(Synonyms).filter(column_name == name).first()
        if query_result:
            if query_result.preferred_name == 1:  # type: ignore
                return str(query_result.lname) if is_lower else str(query_result.name)
            else:
                query_result = (
                    self.session.query(Synonyms)
                    .filter(
                        Synonyms.id == query_result.id, Synonyms.preferred_name == 1
                    )
                    .first()
                )
                if query_result:
                    return (
                        str(query_result.lname) if is_lower else str(query_result.name)
                    )
        return f"<UNMATCHED> {name}"

    def get_synonyms(self, lname: str) -> List[str]:
        """Get the synonyms of a drug from the database.
        It searches the `lname` column and returns all the `name` column values that correspond to its synonyms.
        """
        query_result = (
            self.session.query(Synonyms).filter(Synonyms.lname == lname).all()
        )
        return [str(row.name) for row in query_result]
