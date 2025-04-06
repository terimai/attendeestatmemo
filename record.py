import streamlit as st
import pandas as pd
from typing import List
from model import Person, Organization, Record, RecordPerson
from modelutil import DBSession
from modelutil import get_all_people, get_all_records, remove_records
from modelutil import record_count_group_by_person, record_count_group_by_org
from util import in_db_session

def format_record_person(rp):
    return "{0}({1})".format(rp.person.name, \
                            ', '.join([a.name for a in rp.affiliations]))
def format_record_person_list(rpl: List[RecordPerson]):
    return ', '.join([format_record_person(rp) for rp in rpl])


class Entity_:
    person: Person
    affiliations: List[Organization]
    def __init__(self, p: Person, aff: List[Organization] = []):
        self.person = p
        self.affiliations = aff

SESSION_KEY_ENTITIES = 'entities_in_new_record'

def save_entities_to_session_state(els: List[Entity_]):
    st.session_state[SESSION_KEY_ENTITIES] = [ \
        (e.person.id, [o.id for o in e.affiliations]) \
    for e in els]

def load_entities_from_session_state(s)->List[Entity_]:
    if SESSION_KEY_ENTITIES not in st.session_state:
        st.session_state[SESSION_KEY_ENTITIES] = []
    return [Entity_(s.get(Person, e[0]), \
                    [s.get(Organization, o) for o in e[1]]) \
            for e in st.session_state[SESSION_KEY_ENTITIES]]

# The function edit_entity_list() does not access a database.
# However, edit_entity_list() is required to be called from in_db_session
# because entities includes SQLAlchemy OR-mapped objects.
def remove_from_entity_list(entities)->bool:
    st.subheader('参加者')
    entities_df = pd.DataFrame([[e.person.name, \
                                ', '.join([a.name for a in e.affiliations])] \
                                for e in entities], columns=['名前', '所属'])
    selected_entities = st.dataframe(entities_df, hide_index=True, \
                                     on_select='rerun', \
                                     selection_mode='multi-row')
    selected_entities_rows = selected_entities.selection.rows
    if len(selected_entities_rows) > 0:
        if st.button('削除', key='delete_selected_entities'):
            to_remove = [entities[i] for i in selected_entities_rows]
            for e in to_remove:
                entities.remove(e)
            return True
    return False

# not in_db_session because the session is passed from the caller.
def add_entity_to_list(session: DBSession, selected_entities: List[Entity_], \
                       all_people: List[Person])->Entity_ | None:
    # Since st.selectbox() returns a copy, it does not work to pass
    # a list of OR-mapped objects.
    selected_person_id_list = [e.person.id for e in selected_entities]
    candidate_pair = [ (p.id, p.name) for p in all_people \
                        if p.id not in selected_person_id_list]
    selected_person = st.selectbox('参加者', candidate_pair,index=None, \
                                   format_func=lambda x: x[1])
    if selected_person is not None:
        assert(not selected_person[0] in selected_person_id_list)
        p = session.get(Person, selected_person[0])
        candidate_orgs = [(o.id, o.name) for o in p.affiliations]
        selected_orgs = st.multiselect('グループ', candidate_orgs, \
                                       format_func=lambda x: x[1])
        if st.button('参加者追加'):
            aff = [session.get(Organization, org[0]) for org in selected_orgs]
            newe = Entity_(p, aff)
            return newe

    # TODO: implement
    return None

@in_db_session
def add_record(session: DBSession):
    st.header('記録登録')
    if SESSION_KEY_ENTITIES not in st.session_state:
        st.session_state[SESSION_KEY_ENTITIES] = []  

    persons = get_all_people(session)
    added_entities = load_entities_from_session_state(session)
    print("Start", added_entities)

    if remove_from_entity_list(added_entities):
        save_entities_to_session_state(added_entities)
        st.rerun()
                
    if st.button('クリア'):
        added_entities = []
        st.session_state[SESSION_KEY_ENTITIES] = []
        st.rerun()

    e = add_entity_to_list(session, added_entities, persons)
    if e is not None:
        assert(type(e) == Entity_)
        added_entities.append(e)
        save_entities_to_session_state(added_entities)
        st.rerun()

    with st.form('add_record'):
        taken_date = st.date_input('日付', key='new_date')
        note = st.text_input('備考', key='new_note')     
        add_new_record = st.form_submit_button('記録追加')
    if add_new_record:
        rps = list()
        newrec = Record(id=None, taken_when= taken_date, note=note, \
                        record_person=[])
        for e in added_entities:
            rps.append(RecordPerson(id=None, record_id=None, record=newrec, \
                                    person=e.person, person_id=e.person.id, \
                                    affiliations=e.affiliations))
        for rp in rps:
            newrec.record_person.append(rp)
        session.add(newrec)
        session.flush()
        session.commit()
        del st.session_state[SESSION_KEY_ENTITIES]
        st.rerun()

@in_db_session
def edit_record(session: DBSession):
    st.header('記録一覧')
    recs = get_all_records(session)
    df_recs = pd.DataFrame([[r.id, r.taken_when, \
                             format_record_person_list(r.record_person), \
                            r.note] for r in recs], \
                            columns=["ID", "日付", "`参加者", '備考'])
    selected_rec = st.dataframe(df_recs, hide_index=True, on_select='rerun', \
                                selection_mode='multi-row')
    selected_rec_rows = selected_rec.selection.rows
    if len(selected_rec_rows):
        remove_r = st.button('削除', key='remove_record')
        if remove_r:
            rls = [ recs[ridx] for ridx in selected_rec_rows]
            remove_records(session, rls)
            session.commit()
            st.rerun()

    if len(selected_rec_rows) == 1:
        record: Record = recs[selected_rec_rows[0]]
        st.header('記録 ' + str(record.id) + ' を編集')
        with st.form('edit_date_note'):
            new_date = st.date_input('日付', key='edit_date', \
                                     value=record.taken_when)
            new_note = st.text_input('備考', key='edit_note', \
                                     value=record.note)
            btn_date_note = st.form_submit_button('修正')
        if btn_date_note:
            record.taken_when = new_date
            record.note = new_note
            session.commit()
            st.rerun()
        # TODO: edit record_person        
        entity_list = [Entity_(rp.person, rp.affiliations) \
                       for rp in record.record_person]
        if remove_from_entity_list(entity_list):
            plist = [e.person for e in entity_list]
            to_remove = filter(lambda rp: not rp.person in plist, \
                               record.record_person)
            for rp in to_remove:
                session.delete(rp)
            session.commit()
            st.rerun()
        allp = get_all_people(session)
        e = add_entity_to_list(session, entity_list, allp)
        if e is not None:
            rp = RecordPerson(id=None, record_id=record.id, record=record, \
                              person_id=e.person.id, person=e.person, \
                              affiliations=e.affiliations)
            record.record_person.append(rp)
            session.commit()
            st.rerun()

def show_stat_person(session: DBSession, start_date, end_date):
    result = record_count_group_by_person(session, start_date, end_date)
    df = pd.DataFrame([(r[1].name, r[0]) for r in result], \
                      columns=['人物', '件数'])
    st.dataframe(df, hide_index=True)

def show_stat_group(session: DBSession, start_date, end_date):
    result = record_count_group_by_org(session, start_date, end_date)
    df = pd.DataFrame([(r[1].name, r[0]) for r in result], \
                      columns=['グループ', '件数'])
    st.dataframe(df, hide_index=True)

@in_db_session
def show_stat(session: DBSession):
    st.header('集計')
    col_from, col_to = st.columns(2)
    set_start = col_from.checkbox('開始日を指定',  key='ignore_start_date')
    start_date = col_from.date_input('開始日', key='stat_date_start')
    set_end = col_to.checkbox('終了日を指定', key='ignore_end_date')
    end_date = col_to.date_input('終了日', key='stat_date_end')
    show_stat_person_enabled = st.toggle('人物')
    show_stat_group_enabled = st.toggle('グループ')
    if show_stat_person_enabled or show_stat_group_enabled:
        if st.button('決定'):
            if not set_start:
                start_date = None
            if not set_end:
                end_date = None
            if show_stat_person_enabled:
                show_stat_person(session, start_date, end_date)
            if show_stat_group_enabled:
                show_stat_group(session, start_date, end_date)
