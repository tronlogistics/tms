from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
driver = Table('driver', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('fleet_id', Integer),
    Column('user_id', Integer),
    Column('first_name', String(length=30)),
    Column('last_name', String(length=30)),
    Column('email', String(length=255)),
    Column('phone_area_code', String(length=3)),
    Column('phone_prefix', String(length=3)),
    Column('phone_line_number', String(length=4)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['driver'].columns['email'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['driver'].columns['email'].drop()
