import streamlit as st
import conf
from functools import wraps

def in_db_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = st.connection(conf.DBNAME, type='sql', query_cache_size=0)
        with conn.session as s:
            kwargs['session'] = s
            return func(*args, **kwargs)
    return wrapper