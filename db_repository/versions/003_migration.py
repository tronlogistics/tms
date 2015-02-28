from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
Contact = Table('Contact', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('location_id', INTEGER),
    Column('contact_phone_area_code', VARCHAR(length=3)),
    Column('contact_phone_prefix', VARCHAR(length=3)),
    Column('contact_phone_line_number', VARCHAR(length=4)),
    Column('email', VARCHAR(length=30)),
    Column('name', VARCHAR(length=60)),
    Column('phone', VARCHAR(length=30)),
)

Contact = Table('Contact', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('location_id', Integer),
    Column('name', String(length=60)),
    Column('email', String(length=30)),
    Column('phone', String(length=30)),
    Column('phone_area_code', String(length=3)),
    Column('phone_prefix', String(length=3)),
    Column('phone_line_number', String(length=4)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['Contact'].columns['contact_phone_area_code'].drop()
    pre_meta.tables['Contact'].columns['contact_phone_line_number'].drop()
    pre_meta.tables['Contact'].columns['contact_phone_prefix'].drop()
    post_meta.tables['Contact'].columns['phone_area_code'].create()
    post_meta.tables['Contact'].columns['phone_line_number'].create()
    post_meta.tables['Contact'].columns['phone_prefix'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['Contact'].columns['contact_phone_area_code'].create()
    pre_meta.tables['Contact'].columns['contact_phone_line_number'].create()
    pre_meta.tables['Contact'].columns['contact_phone_prefix'].create()
    post_meta.tables['Contact'].columns['phone_area_code'].drop()
    post_meta.tables['Contact'].columns['phone_line_number'].drop()
    post_meta.tables['Contact'].columns['phone_prefix'].drop()
