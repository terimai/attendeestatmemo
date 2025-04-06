import streamlit as st

from entity import add_entity, edit_entities
from record import add_record, edit_record, show_stat

st.title('Test')
st.cache_data.clear()
st.title('参加記録')
modes = [('New Entity', add_entity),
         ('New Record', add_record),
         ('Manage Entities', edit_entities),
         ('Manage Record', edit_record),
         ('Show Statistics', show_stat)
         ]
mode = st.sidebar.radio('Mode',  list(range(len(modes))),
                            format_func=lambda i: modes[i][0])
if mode is not None:
    modes[mode][1]()
