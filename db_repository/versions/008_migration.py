from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
LocationStatus = Table('LocationStatus', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('location_id', Integer),
    Column('status', String(length=20)),
    Column('created_on', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['LocationStatus'].columns['created_on'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['LocationStatus'].columns['created_on'].drop()
