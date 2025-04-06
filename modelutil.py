from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

DBSession = Session

from model import Organization, Person
from model import Record, RecordPerson, record_person_affiliations

def _get_all_obj(cls: type, session: Session):
    stmt = select(cls)
    return [ o[0] for o in session.execute(stmt).all()]

def get_all_organizations(session: Session)->List[Organization]:
    return _get_all_obj(Organization, session)

def get_all_persons(session: Session)->List[Person]:
    return _get_all_obj(Person, session)

def get_all_people(session: Session)->List[Person]:
    return get_all_persons(session)

def get_all_records(session: Session)->List[Record]:
    return _get_all_obj(Record, session)

def remove_record(session: Session, r: Record):
    for rp in r.record_person:
        session.delete(rp)
    session.delete(r)

def remove_records(session: Session, rls: List[Record]):
    for r in rls:
        remove_record(session, r)

def append_start_end_filter(stmt, start_date: Optional[datetime.date], \
                            end_date: Optional[datetime.date]):
    if start_date is not None:
        stmt = stmt.filter(Record.taken_when >= start_date)
    if end_date is not None:
        stmt = stmt.filter(Record.taken_when <= end_date)
    return stmt

def record_count_group_by_person(session: Session, \
                                start_date: Optional[datetime.date], \
                                end_date: Optional[datetime.date]):
    stmt = session.query(func.count(Record.id).label('record_count'), \
                         Person) \
                        .join(RecordPerson, \
                                   Record.id==RecordPerson.record_id) \
                        .group_by(RecordPerson.person_id) \
                        .join(Person, RecordPerson.person_id == Person.id)
    stmt = append_start_end_filter(stmt, start_date, end_date) \
        .order_by(desc('record_count'))
    res = session.execute(stmt).all()
    return res

def record_count_group_by_org(session: Session, \
                              start_date: Optional[datetime.date], \
                              end_date: Optional[datetime.date]):
    stmt = session.query(func.count(Record.id).label('record_count'), \
                         Organization) \
                        .join(RecordPerson, \
                              Record.id == RecordPerson.record_id) \
                        .join(record_person_affiliations, \
                               RecordPerson.id == record_person_affiliations \
                                                  .c.record_person_id) \
                        .group_by(record_person_affiliations.c.organization_id) \
                        .join(Organization, \
                              record_person_affiliations.c.organization_id \
                                == Organization.id)
    stmt = append_start_end_filter(stmt, start_date, end_date) \
        .order_by(desc('record_count'))
    print(stmt)
    res = session.execute(stmt).all()
    return res

