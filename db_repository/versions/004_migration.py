from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
load_detail = Table('load_detail', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('pickup_id', INTEGER),
    Column('delivery_id', INTEGER),
    Column('weight', INTEGER),
    Column('dim_length', INTEGER),
    Column('dim_width', INTEGER),
    Column('dim_height', INTEGER),
    Column('approx_miles', INTEGER),
    Column('number_pieces', INTEGER),
)

load_detail = Table('load_detail', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('location_id', Integer),
    Column('type', String(length=10)),
    Column('weight', Integer),
    Column('dim_length', Integer),
    Column('dim_width', Integer),
    Column('dim_height', Integer),
    Column('approx_miles', Integer),
    Column('number_pieces', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['load_detail'].columns['delivery_id'].drop()
    pre_meta.tables['load_detail'].columns['pickup_id'].drop()
    post_meta.tables['load_detail'].columns['location_id'].create()
    post_meta.tables['load_detail'].columns['type'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['load_detail'].columns['delivery_id'].create()
    pre_meta.tables['load_detail'].columns['pickup_id'].create()
    post_meta.tables['load_detail'].columns['location_id'].drop()
    post_meta.tables['load_detail'].columns['type'].drop()
