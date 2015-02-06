from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
lane = Table('lane', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('load_id', INTEGER),
    Column('origin_id', INTEGER),
    Column('destination_id', INTEGER),
)

location = Table('location', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('lane_id', Integer),
    Column('address1', String(length=100)),
    Column('address2', String(length=100)),
    Column('city', String(length=100)),
    Column('state', String(length=80)),
    Column('postal_code', Integer),
    Column('latitude', Float(precision=6)),
    Column('longitude', Float(precision=6)),
    Column('contact_name', String(length=60)),
    Column('contact_email', String(length=30)),
    Column('contact_phone', String(length=30)),
    Column('contact_phone_area_code', String(length=3)),
    Column('contact_phone_prefix', String(length=3)),
    Column('contact_phone_line_number', String(length=4)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['lane'].columns['destination_id'].drop()
    pre_meta.tables['lane'].columns['origin_id'].drop()
    post_meta.tables['location'].columns['lane_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['lane'].columns['destination_id'].create()
    pre_meta.tables['lane'].columns['origin_id'].create()
    post_meta.tables['location'].columns['lane_id'].drop()
