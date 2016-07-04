import os
import unittest
import sys
from werkzeug import generate_password_hash
 
topdir = os.path.join(os.path.dirname(__file__), "../..")
sys.path.append(topdir)

from app import db, app
from app.models.user import User
from app.models.company import Company
from app.models.address import Address
from app.models.role import Role
from config import basedir
 
class BaseAuthTestCase(unittest.TestCase):
 
    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        self.db = db
        self.db.create_all()
 
        if User.query.filter_by(email='admin@admin.local').count() == 0:
            self.user = User(email='admin@admin.local',
                                first_name='admin',
                                last_name='admin',
                                phone="1234567890",
                                password='admin')
            address = Address("add1", "city", "state", "60010")
            company = Company("1", "Test", address, "broker")
            self.user.company = company
            db.session.add(self.user)
            db.session.add(company)
            

        role1 = Role(code="admin", name="Admin")
        role2 = Role(code="shipper", name="Shipper")
        role3 = Role(code="broker", name="Broker")
        role4 = Role(code="company_admin", name="Company Admin")
        role5 = Role(code="driver", name="Driver")
        role6 = Role(code="owner_operator", name="Onwer Operator")
        db.session.add(role1)
        db.session.add(role2)
        db.session.add(role3)
        db.session.add(role4)
        db.session.add(role5)
        db.session.add(role6)

        db.session.commit()
 
    def tearDown(self):
        db.session.remove()
        db.drop_all()
 
    if __name__ == '__main__':
        unittest.main()