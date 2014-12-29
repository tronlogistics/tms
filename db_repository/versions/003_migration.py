from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
assigned_users = Table('assigned_users', pre_meta,
    Column('user_id', INTEGER),
    Column('load_id', INTEGER),
)

bid = Table('bid', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('load_id', INTEGER),
    Column('offered_by_id', INTEGER),
    Column('offered_to_id', INTEGER),
    Column('value', FLOAT),
    Column('status', VARCHAR(length=10)),
)

driver = Table('driver', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('fleet_id', INTEGER),
    Column('user_id', INTEGER),
    Column('first_name', VARCHAR(length=30)),
    Column('last_name', VARCHAR(length=30)),
    Column('phone_area_code', VARCHAR(length=3)),
    Column('phone_prefix', VARCHAR(length=3)),
    Column('phone_line_number', VARCHAR(length=4)),
)

fleet = Table('fleet', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('user_id', INTEGER),
)

lane = Table('lane', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('load_id', INTEGER),
    Column('origin_id', INTEGER),
    Column('destination_id', INTEGER),
)

load = Table('load', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('user_id', INTEGER),
    Column('name', VARCHAR(length=80)),
    Column('status', VARCHAR(length=20)),
    Column('broker_id', INTEGER),
    Column('carrier_id', INTEGER),
    Column('carrier_cost', FLOAT),
    Column('price', FLOAT),
    Column('description', VARCHAR(length=250)),
    Column('driver_id', INTEGER),
)

load_detail = Table('load_detail', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('weight', INTEGER),
    Column('dim_length', INTEGER),
    Column('dim_width', INTEGER),
    Column('dim_height', INTEGER),
    Column('approx_miles', INTEGER),
    Column('number_pieces', INTEGER),
    Column('comments', VARCHAR(length=500)),
    Column('load_id', INTEGER),
    Column('pickup_date', DATE),
    Column('delivery_date', DATE),
    Column('trailer_group', VARCHAR(length=20)),
    Column('trailer_type', VARCHAR(length=20)),
    Column('load_type', VARCHAR(length=20)),
    Column('total_miles', INTEGER),
    Column('purchase_order', VARCHAR(length=20)),
    Column('over_dimensional', BOOLEAN),
)

location = Table('location', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('address1', VARCHAR(length=100)),
    Column('address2', VARCHAR(length=100)),
    Column('city', VARCHAR(length=100)),
    Column('state', VARCHAR(length=80)),
    Column('postal_code', INTEGER),
    Column('latitude', FLOAT),
    Column('longitude', FLOAT),
    Column('contact_name', VARCHAR(length=60)),
    Column('contact_email', VARCHAR(length=30)),
    Column('contact_phone', VARCHAR(length=30)),
    Column('contact_phone_area_code', VARCHAR(length=3)),
    Column('contact_phone_prefix', VARCHAR(length=3)),
    Column('contact_phone_line_number', VARCHAR(length=4)),
)

truck = Table('truck', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('user_id', INTEGER),
    Column('fleet_id', INTEGER),
    Column('driver_id', INTEGER),
    Column('name', VARCHAR(length=100)),
    Column('latitude', FLOAT),
    Column('longitude', FLOAT),
    Column('is_available', BOOLEAN),
    Column('trailer_group', VARCHAR(length=30)),
    Column('trailer_type', VARCHAR(length=30)),
    Column('max_weight', INTEGER),
    Column('dim_length', INTEGER),
    Column('dim_height', INTEGER),
    Column('dim_width', INTEGER),
)

user_to_user = Table('user_to_user', pre_meta,
    Column('left_user_id', INTEGER, primary_key=True, nullable=False),
    Column('right_user_id', INTEGER, primary_key=True, nullable=False),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['assigned_users'].drop()
    pre_meta.tables['bid'].drop()
    pre_meta.tables['driver'].drop()
    pre_meta.tables['fleet'].drop()
    pre_meta.tables['lane'].drop()
    pre_meta.tables['load'].drop()
    pre_meta.tables['load_detail'].drop()
    pre_meta.tables['location'].drop()
    pre_meta.tables['truck'].drop()
    pre_meta.tables['user_to_user'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['assigned_users'].create()
    pre_meta.tables['bid'].create()
    pre_meta.tables['driver'].create()
    pre_meta.tables['fleet'].create()
    pre_meta.tables['lane'].create()
    pre_meta.tables['load'].create()
    pre_meta.tables['load_detail'].create()
    pre_meta.tables['location'].create()
    pre_meta.tables['truck'].create()
    pre_meta.tables['user_to_user'].create()
