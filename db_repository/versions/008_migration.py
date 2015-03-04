from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
Location = Table('Location', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('lane_id', Integer),
    Column('contact_id', Integer),
    Column('pickup_id', Integer),
    Column('delivery_id', Integer),
    Column('stop_number', Integer),
    Column('arrival_date', Date),
    Column('status', String(length=20)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['Location'].columns['status'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['Location'].columns['status'].drop()
