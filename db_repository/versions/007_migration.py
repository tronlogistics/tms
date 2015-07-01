from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
LocationStatus = Table('LocationStatus', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('location_id', Integer),
    Column('status', String(length=20)),
)

Location = Table('Location', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('lane_id', INTEGER),
    Column('pickup_id', INTEGER),
    Column('delivery_id', INTEGER),
    Column('contact_id', INTEGER),
    Column('stop_number', VARCHAR(length=10)),
    Column('arrival_date', DATE),
    Column('type', VARCHAR(length=10)),
    Column('status', VARCHAR(length=20)),
    Column('latitude', FLOAT),
    Column('longitude', FLOAT),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['LocationStatus'].create()
    pre_meta.tables['Location'].columns['status'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['LocationStatus'].drop()
    pre_meta.tables['Location'].columns['status'].create()
