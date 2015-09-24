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
    Column('driver_type', VARCHAR(length=30)),
    Column('email', VARCHAR(length=255)),
    Column('phone', VARCHAR(length=14)),
    Column('linked_account', BOOLEAN),
)

User = Table('User', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('company_id', Integer),
    Column('password', String(length=255), nullable=False),
    Column('email', String(length=255), nullable=False),
    Column('confirmed_at', DateTime),
    Column('authenticated', Boolean, nullable=False),
    Column('name', String(length=100), nullable=False),
    Column('disabled', Boolean),
    Column('customer_id', Integer),
    Column('driver_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['Driver'].columns['user_id'].drop()
    post_meta.tables['User'].columns['driver_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['Driver'].columns['user_id'].create()
    post_meta.tables['User'].columns['driver_id'].drop()
