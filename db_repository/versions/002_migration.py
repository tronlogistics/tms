from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
BOL = Table('BOL', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('number', String(length=20)),
    Column('number_units', Integer),
    Column('weight', String(length=7)),
    Column('commodity_type', String(length=255)),
    Column('dim_length', String(length=7)),
    Column('dim_length_type', String(length=7)),
    Column('dim_width', String(length=7)),
    Column('dim_width_type', String(length=7)),
    Column('dim_height', String(length=7)),
    Column('dim_height_type', String(length=7)),
)

detail_to_BOL = Table('detail_to_BOL', post_meta,
    Column('detail_id', Integer),
    Column('BOL_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['BOL'].create()
    post_meta.tables['detail_to_BOL'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['BOL'].drop()
    post_meta.tables['detail_to_BOL'].drop()
