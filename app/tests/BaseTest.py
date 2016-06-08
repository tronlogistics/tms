import os
import unittest
import sys
from werkzeug import generate_password_hash
 
topdir = os.path.join(os.path.dirname(__file__), "../..")
sys.path.append(topdir)

from app import db, app
from app.models.user import User
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
            db.session.add(self.user)
            db.session.commit()
 
    def tearDown(self):
        db.session.remove()
        db.drop_all()
 
    if __name__ == '__main__':
        unittest.main()