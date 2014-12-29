from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
bid = Table('bid', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('load_id', Integer),
    Column('offered_by_id', Integer),
    Column('offered_to_id', Integer),
    Column('value', Float(precision=3)),
    Column('status', String(length=10)),
)

driver = Table('driver', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('fleet_id', Integer),
    Column('user_id', Integer),
    Column('first_name', String(length=30)),
    Column('last_name', String(length=30)),
    Column('phone_area_code', String(length=3)),
    Column('phone_prefix', String(length=3)),
    Column('phone_line_number', String(length=4)),
)

fleet = Table('fleet', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
)

lane = Table('lane', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('load_id', Integer),
    Column('origin_id', Integer),
    Column('destination_id', Integer),
)

load = Table('load', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('name', String(length=80)),
    Column('status', String(length=20)),
    Column('broker_id', Integer),
    Column('carrier_id', Integer),
    Column('carrier_cost', Float(precision=3)),
    Column('price', Float(precision=3)),
    Column('description', String(length=250)),
    Column('driver_id', Integer),
)

load_detail = Table('load_detail', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('weight', Integer),
    Column('dim_length', Integer),
    Column('dim_width', Integer),
    Column('dim_height', Integer),
    Column('approx_miles', Integer),
    Column('number_pieces', Integer),
    Column('comments', String(length=500)),
    Column('load_id', Integer),
    Column('pickup_date', Date),
    Column('delivery_date', Date),
    Column('trailer_group', String(length=20)),
    Column('trailer_type', String(length=20)),
    Column('load_type', String(length=20)),
    Column('total_miles', Integer),
    Column('purchase_order', String(length=20)),
    Column('over_dimensional', Boolean),
)

location = Table('location', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('address1', String(length=100)),
    Column('address2', String(length=100)),
    Column('city', String(length=100)),
    Column('state', String(length=80)),
    Column('postal_code', Integer),
    Column('latitude', Float(precision=6)),
    Column('longitude', Float(precision=6)),
    Column('contact_name', String(length=60)),
    Column('contact_email', String(length=30)),
    Column('contact_phone', String(length=30)),
    Column('contact_phone_area_code', String(length=3)),
    Column('contact_phone_prefix', String(length=3)),
    Column('contact_phone_line_number', String(length=4)),
)

truck = Table('truck', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('fleet_id', Integer),
    Column('driver_id', Integer),
    Column('name', String(length=100)),
    Column('latitude', Float(precision=6)),
    Column('longitude', Float(precision=6)),
    Column('is_available', Boolean),
    Column('trailer_group', String(length=30)),
    Column('trailer_type', String(length=30)),
    Column('max_weight', Integer),
    Column('dim_length', Integer),
    Column('dim_height', Integer),
    Column('dim_width', Integer),
)

user_to_user = Table('user_to_user', post_meta,
    Column('left_user_id', Integer, primary_key=True, nullable=False),
    Column('right_user_id', Integer, primary_key=True, nullable=False),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['bid'].create()
    post_meta.tables['driver'].create()
    post_meta.tables['fleet'].create()
    post_meta.tables['lane'].create()
    post_meta.tables['load'].create()
    post_meta.tables['load_detail'].create()
    post_meta.tables['location'].create()
    post_meta.tables['truck'].create()
    post_meta.tables['user_to_user'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['bid'].drop()
    post_meta.tables['driver'].drop()
    post_meta.tables['fleet'].drop()
    post_meta.tables['lane'].drop()
    post_meta.tables['load'].drop()
    post_meta.tables['load_detail'].drop()
    post_meta.tables['location'].drop()
    post_meta.tables['truck'].drop()
    post_meta.tables['user_to_user'].drop()
