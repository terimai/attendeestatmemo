from sqlalchemy import create_engine
import model
import tomllib
from os.path import expanduser
from pathlib import PurePath
import conf

CONFFILE = PurePath('.', '.streamlit', 'secrets.toml')
# TODO: if secrets.toml is not found in ./.streamlit,
#       find it in a user profile directory
# CONFFILE = expanduser(PurePath('.', '.streamlit', 'secrets.toml'))

with open(CONFFILE, 'rb') as fh:
    cf = tomllib.load(fh)
    dburl = cf['connections'][conf.DBNAME]['url']
    engine = create_engine(dburl)

    model.Base.metadata.create_all(engine)