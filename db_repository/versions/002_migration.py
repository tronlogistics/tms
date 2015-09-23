from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
Load = Table('Load', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('broker_id', Integer),
    Column('shipper_id', Integer),
    Column('name', String(length=80)),
    Column('status', String(length=150)),
    Column('trailer_group', String(length=150)),
    Column('trailer_type', String(length=150)),
    Column('load_type', String(length=150)),
    Column('total_miles', Integer),
    Column('carrier_cost', String(length=150)),
    Column('price', String(length=150)),
    Column('description', String(length=250)),
    Column('comments', String(length=500)),
    Column('truck_id', Integer),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['Load'].columns['user_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['Load'].columns['user_id'].drop()
