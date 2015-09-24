from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
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
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['User'].columns['disabled'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['User'].columns['disabled'].drop()
