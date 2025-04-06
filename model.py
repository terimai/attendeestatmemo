from typing import List, Optional
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy import Date, Integer
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.associationproxy import AssociationProxy
import datetime

class Base(DeclarativeBase, MappedAsDataclass):
    pass

affiliation_table = Table(
    'affiliation', Base.metadata,
    Column('person_id', ForeignKey('person.id'), primary_key=True),
    Column('organization_id', ForeignKey('organization.id'), primary_key=True),
)

class Organization(Base):
    __tablename__ = 'organization'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    members: Mapped[List["Person"]] = relationship( \
        secondary=affiliation_table, back_populates='affiliations')

class Person(Base):
    __tablename__ = 'person'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    affiliations: Mapped[List["Organization"]] = relationship( \
        secondary=affiliation_table, back_populates='members')


class Record(Base):
    __tablename__ = 'record'
    id: Mapped[int] = mapped_column(primary_key=True)
    taken_when: Mapped[datetime.date] = mapped_column(Date)
    note: Mapped[Optional[str]] = mapped_column()
    record_person: Mapped[List["RecordPerson"]] \
        = relationship(back_populates='record')

record_person_affiliations = Table(
    'record_person_affiliation', Base.metadata,
    Column('record_person_id', Integer, ForeignKey('record_person.id'), primary_key=True),
    Column('organization_id', Integer, ForeignKey('organization.id'), primary_key=True)
)

class RecordPerson(Base):
    __tablename__ = 'record_person'
    id: Mapped[int] = mapped_column(primary_key=True)
    record_id: Mapped[int] = mapped_column(ForeignKey('record.id'))
    person_id: Mapped[int] = mapped_column(ForeignKey('person.id'))
    record: Mapped[Record] = relationship( \
        back_populates='record_person',)
    person: Mapped[Person] = relationship()
    affiliations: Mapped[List[Organization]] = relationship(secondary=record_person_affiliations)

