from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
assigned_Contacts = Table('assigned_Contacts', post_meta,
    Column('Contact_id', Integer),
    Column('load_id', Integer),
)

Load = Table('Load', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('broker_id', Integer),
    Column('name', String(length=80)),
    Column('status', String(length=20)),
    Column('trailer_group', String(length=20)),
    Column('trailer_type', String(length=20)),
    Column('load_type', String(length=20)),
    Column('total_miles', Integer),
    Column('purchase_order', String(length=20)),
    Column('over_dimensional', Boolean),
    Column('carrier_cost', Float(precision=3)),
    Column('price', Float(precision=3)),
    Column('description', String(length=250)),
    Column('comments', String(length=500)),
    Column('driver_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['assigned_Contacts'].create()
    post_meta.tables['Load'].columns['broker_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['assigned_Contacts'].drop()
    post_meta.tables['Load'].columns['broker_id'].drop()
