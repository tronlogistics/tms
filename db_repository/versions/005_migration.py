from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
Client = Table('Client', post_meta,
    Column('name', String(length=40)),
    Column('description', String(length=400)),
    Column('user_id', Integer),
    Column('client_id', String(length=40), primary_key=True, nullable=False),
    Column('client_secret', String(length=55), nullable=False),
    Column('is_confidential', Boolean),
    Column('_redirect_uris', Text),
    Column('_default_scopes', Text),
)

Gant = Table('Gant', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('client_id', String(length=40), nullable=False),
    Column('code', String(length=255), nullable=False),
    Column('redirect_uri', String(length=255)),
    Column('expires', DateTime),
    Column('_scopes', Text),
)

token = Table('token', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('client_id', String(length=40), nullable=False),
    Column('user_id', Integer),
    Column('token_type', String(length=40)),
    Column('access_token', String(length=255)),
    Column('refresh_token', String(length=255)),
    Column('expires', DateTime),
    Column('_scopes', Text),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['Client'].create()
    post_meta.tables['Gant'].create()
    post_meta.tables['token'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['Client'].drop()
    post_meta.tables['Gant'].drop()
    post_meta.tables['token'].drop()
