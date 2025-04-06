import streamlit as st
import pandas as pd
from model import Person, Organization
from modelutil import get_all_organizations, get_all_people, DBSession
from util import in_db_session

@in_db_session
def add_org(session: DBSession):
    organizations = get_all_organizations(session)

    st.header('グループ登録')

    with st.form('add_organization'):
            neworgname = st.text_input('グループ名')
            add_neworg = st.form_submit_button('追加')

    if add_neworg:
        neworg = Organization(id=None, name=neworgname, members=[])
        session.add(neworg)
        session.flush()
        session.commit()
        st.rerun()

@in_db_session
def add_person(session: DBSession):
    persons = get_all_people(session)
    organizations = get_all_organizations(session)
    st.header('人物登録')
    with st.form('add_person'):
        newpersonname = st.text_input('人名')
        candidate_orgs = [(o.id, o.name) for o in organizations]
        selected = st.multiselect('所属', candidate_orgs, \
                                    format_func=lambda x: x[1])
        add_newperson = st.form_submit_button('追加')

    newaff = [session.get(Organization, o[0]) for o in selected]
    if add_newperson:
        newp = Person(id=None, name=newpersonname, affiliations=newaff)
        session.add(newp)
        session.flush()
        session.commit()
        st.rerun()


def add_entity():
    e = st.segmented_control('what entity to add', \
                         [('グループ', add_org), ('人物', add_person)],
                         format_func=lambda e: e[0])
    if e is not None:
        e[1]()          

@in_db_session
def edit_entities(session: DBSession):
    st.header('人物・グループ一覧')
    orgs = get_all_organizations(session)
    people = get_all_people(session)
    st.subheader('グループ')

    df_orgs = pd.DataFrame([[o.name, ', '.join([m.name for m in o.members])] \
                            for o in orgs], columns=['名前', 'メンバー'])
    selected_org = st.dataframe(df_orgs, hide_index=True, on_select='rerun', \
                                selection_mode='single-row')
    selected_org_rows = selected_org.selection.rows
    assert(len(selected_org_rows) <= 1)
    if len(selected_org_rows) == 1:
        org = orgs[selected_org_rows[0]]
        st.write(org.name + ' を編集')
        # remove is not supporeted.
        with st.form('edit_org_name'):
            new_org_name = st.text_input('名称')
            fix_org_name = st.form_submit_button('名称を修正')
        if fix_org_name:
            org.name = new_org_name
            session.commit()
            st.rerun()

    st.subheader('人物')   
    df_people = pd.DataFrame([[p.name, \
                            ', '.join([a.name for a in p.affiliations])] \
                               for p in people], columns=['名前', '所属'])
    selected_person = st.dataframe(df_people, hide_index=True, \
                                    on_select='rerun', \
                                    selection_mode='single-row')
    selected_person_rows = selected_person.selection.rows
    assert(len(selected_person_rows) <= 1)
    if len(selected_person_rows) == 1:
        p = people[selected_person_rows[0]]
        st.write(p.name + ' を編集')
        # remove is not supported

        with st.form('edit_person_name'):
            new_person_name = st.text_input('名前')
            fix_person_name = st.form_submit_button('名前を修正')
        if fix_person_name:
            p.name = new_person_name
            session.commit()
            st.rerun()
        aff = [(o.id, o.name) for o in p.affiliations]
        with st.form('edit_person_affiliation'):
            candidate_orgs = [(o.id, o.name) for o in orgs]
            selected = st.multiselect('所属', candidate_orgs, default=aff, \
                                        format_func=lambda o: o[1])
            fix_person_affiliations = st.form_submit_button('所属を修正')
        if fix_person_affiliations and selected != aff:
            aff_set = set(aff)
            selected_set = set(selected)
            for a in selected_set - aff_set:
                p.affiliations.append(session.get(Organization, a[0]))
            for a in aff_set - selected_set:
                p.affiliations.remove(session.get(Organization, a[0]))
            session.commit()
            st.rerun()
                

