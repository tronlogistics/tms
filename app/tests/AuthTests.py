import flask
import unittest
import BaseTest
from app.models.user import User
from datetime import timedelta
 
class AuthTests(BaseTest.BaseAuthTestCase):
 
    def login(self, email, password):
        return self.app.post('/u/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)
 
    def logout(self):
        return self.app.get('/u/logout', follow_redirects=True)
 
    #def create(self, name, email, password, password_confirm, description):
    #    return self.app.post('user/create', data=dict(
    #        name=name,
    #        email=email,
    #        password=password,
    #        password_confirm=password_confirm,
    #        description=description
    #    ), follow_redirects=True)
 
    def test_page_not_found(self):
        """Pages which dont exist should be directed to a 404 page"""
        rv = self.app.get('/a-page-which-doesnt-exist')
        self.assertRaises(404)
 
    def test_sign_in_page_loads(self):
        """Sign in page loads successfully"""
        rv = self.app.get('u/login')
        self.assertTrue(b'Sign in' in rv.data)
 
    def test_login_without_confirmed_account(self):
        """Should display not confirmed message"""
        rv = self.login('admin@admin.local', 'admin')
        print rv.data
        self.assertTrue(b'"You must confirm your e-mail' in rv.data)

    def test_login_with_confirmed_account(self):
        """Should display successfully logged in message"""
        #self.user.confirmed_at = INSERT
        rv = self.login('admin@admin.local', 'admin')
        self.assertTrue(b'"You must confirm your e-mail' in rv.data)
 
    #def test_login_success_session(self):
    #    """Successfull login should put user_name in session"""
    #    with self.app as c:
    #        rv = self.login('admin@admin.local', 'default')
    #        self.assertTrue(0 == self.user)
 
#    def test_logout_success(self):
#        """Successfull logout should remove user-name from session"""
#        with self.app as c:
#            self.login('admin@admin.local', 'default')
#            rv = self.logout()
#            self.assertTrue('user_name' not in flask.session)
 
    def test_login_failed_bad_password(self):
        """Failed Logins with bad password should display failure message"""
        rv = self.login('admin@admin.local', 'bad_password')
        self.assertTrue(b'Invalid Password.' in rv.data)
 
    def test_login_failed_bad_email(self):
        """Failed Logins with bad email should display failure message"""
        rv = self.login('bad_email', 'admin')
        self.assertTrue(b'This email is not registered.' in rv.data)
 
    #def test_user_creation_success(self):
    #    """User should be found in the database after creation"""
    #    with self.app as c:
    #        self.create('test',
    #            'test@admin.local',
    #            'secret',
    #            'secret',
    #            'A test user')
 
    #        user = Users.query.filter_by(email='test@admin.local').count()
    #        self.assertTrue(user == 1)
 
 
 
if __name__ == '__main__':
    unittest.main()