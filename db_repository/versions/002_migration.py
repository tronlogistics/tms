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
    Column('over_dimensional', Boolean),
    Column('carrier_invoice', String(length=150)),
    Column('broker_invoice', String(length=150)),
    Column('description', String(length=250)),
    Column('comments', String(length=500)),
    Column('max_weight', String(length=7)),
    Column('max_width', String(length=7)),
    Column('max_width_type', String(length=7)),
    Column('max_length', String(length=7)),
    Column('max_length_type', String(length=7)),
    Column('max_height', String(length=7)),
    Column('max_height_type', String(length=7)),
    Column('truck_id', Integer),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['Load'].columns['max_height'].create()
    post_meta.tables['Load'].columns['max_height_type'].create()
    post_meta.tables['Load'].columns['max_length'].create()
    post_meta.tables['Load'].columns['max_length_type'].create()
    post_meta.tables['Load'].columns['max_weight'].create()
    post_meta.tables['Load'].columns['max_width'].create()
    post_meta.tables['Load'].columns['max_width_type'].create()
    post_meta.tables['Load'].columns['over_dimensional'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['Load'].columns['max_height'].drop()
    post_meta.tables['Load'].columns['max_height_type'].drop()
    post_meta.tables['Load'].columns['max_length'].drop()
    post_meta.tables['Load'].columns['max_length_type'].drop()
    post_meta.tables['Load'].columns['max_weight'].drop()
    post_meta.tables['Load'].columns['max_width'].drop()
    post_meta.tables['Load'].columns['max_width_type'].drop()
    post_meta.tables['Load'].columns['over_dimensional'].drop()
