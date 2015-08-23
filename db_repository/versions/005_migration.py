from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
Driver = Table('Driver', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('fleet_id', INTEGER),
    Column('user_id', INTEGER),
    Column('truck_id', INTEGER),
    Column('first_name', VARCHAR(length=30)),
    Column('last_name', VARCHAR(length=30)),
    Column('email', VARCHAR(length=255)),
    Column('phone_area_code', VARCHAR(length=3)),
    Column('phone_prefix', VARCHAR(length=3)),
    Column('phone_line_number', VARCHAR(length=4)),
)

Driver = Table('Driver', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('fleet_id', Integer),
    Column('user_id', Integer),
    Column('truck_id', Integer),
    Column('first_name', String(length=30)),
    Column('last_name', String(length=30)),
    Column('email', String(length=255)),
    Column('phone', String(length=10)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['Driver'].columns['phone_area_code'].drop()
    pre_meta.tables['Driver'].columns['phone_line_number'].drop()
    pre_meta.tables['Driver'].columns['phone_prefix'].drop()
    post_meta.tables['Driver'].columns['phone'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['Driver'].columns['phone_area_code'].create()
    pre_meta.tables['Driver'].columns['phone_line_number'].create()
    pre_meta.tables['Driver'].columns['phone_prefix'].create()
    post_meta.tables['Driver'].columns['phone'].drop()
