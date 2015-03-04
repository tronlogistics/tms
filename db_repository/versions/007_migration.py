from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
LoadDetail = Table('LoadDetail', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('type', String(length=10)),
    Column('weight', Integer),
    Column('dim_length', Integer),
    Column('dim_width', Integer),
    Column('dim_height', Integer),
    Column('approx_miles', Integer),
    Column('number_pieces', Integer),
    Column('notes', String(length=500)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['LoadDetail'].columns['notes'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['LoadDetail'].columns['notes'].drop()
