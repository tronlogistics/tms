from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
Location = Table('Location', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('lane_id', INTEGER),
    Column('notes', VARCHAR(length=1333)),
    Column('pickup_id', INTEGER),
    Column('delivery_id', INTEGER),
    Column('contact_id', INTEGER),
    Column('stop_number', INTEGER),
    Column('arrival_date', DATE),
    Column('type', VARCHAR(length=10)),
    Column('latitude', FLOAT),
    Column('longitude', FLOAT),
)

Location = Table('Location', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('lane_id', Integer),
    Column('notes', String(length=1333)),
    Column('stop_type', String(length=20)),
    Column('contact_id', Integer),
    Column('stop_number', Integer),
    Column('arrival_date', Date),
    Column('type', String(length=10)),
    Column('latitude', Float(precision=6)),
    Column('longitude', Float(precision=6)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['Location'].columns['delivery_id'].drop()
    pre_meta.tables['Location'].columns['pickup_id'].drop()
    post_meta.tables['Location'].columns['stop_type'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['Location'].columns['delivery_id'].create()
    pre_meta.tables['Location'].columns['pickup_id'].create()
    post_meta.tables['Location'].columns['stop_type'].drop()
