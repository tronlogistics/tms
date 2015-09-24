from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
migration_tmp = Table('migration_tmp', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('fleet_id', INTEGER),
    Column('truck_id', INTEGER),
    Column('first_name', VARCHAR(length=30)),
    Column('last_name', VARCHAR(length=30)),
    Column('driver_type', VARCHAR(length=30)),
    Column('email', VARCHAR(length=255)),
    Column('phone', VARCHAR(length=14)),
    Column('linked_account', BOOLEAN),
)

Driver = Table('Driver', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('fleet_id', Integer),
    Column('truck_id', Integer),
    Column('first_name', String(length=30)),
    Column('last_name', String(length=30)),
    Column('driver_type', String(length=30)),
    Column('email', String(length=255)),
    Column('phone', String(length=14)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['migration_tmp'].drop()
    post_meta.tables['Driver'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['migration_tmp'].create()
    post_meta.tables['Driver'].drop()
