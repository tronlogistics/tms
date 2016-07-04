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

    def register(self, company_name, first_name, last_name, address1, city, state, postal_code,
                    mco, email, phone_number, password, confirm, account_type):
        return self.app.post('/u/register', data=dict(
            company_name=company_name,
            first_name=first_name,
            last_name=last_name,
            address1=address1,
            city=city,
            state=state,
            postal_code=postal_code,
            mco=mco,
            email=email,
            phone_number=phone_number,
            password=password,
            confirm=confirm,
            account_type=account_type
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
        self.assertTrue(b'You must confirm your e-mail' in rv.data)

    def test_login_with_confirmed_account(self):
        """Should display successfully logged in message"""
        self.user.activate()
        rv = self.login('admin@admin.local', 'admin')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(self.user.is_authenticated())
 
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
 
    def test_user_creation_success(self):
        """User should be found in the database after creation"""
        rv = self.register("company_name", "first_name", "last_name", 
                        "address1", "city", "IL", "postal_code",
                        "mco", "email@email.com", "phone_number", "password", 
                        "password", "broker")
        user = User.query.filter_by(email='email@email.com').count()
        self.assertTrue(user == 1)

    def test_user_creation_with_duplicate_email_fails(self):
        """User who registers with a duplicate email should not be allowed"""
        rv = self.register("company_name", "first_name", "last_name", 
                        "address1", "city", "IL", "postal_code",
                        "mco", "email@email.com", "phone_number", "password", 
                        "password", "broker")
        rv = self.register("company_name", "first_name", "last_name", 
                        "address1", "city", "IL", "postal_code",
                        "mco", "email@email.com", "phone_number", "password", 
                        "password", "broker")
        user = User.query.filter_by(email='email@email.com').count()
        self.assertTrue(user == 1)

    def test_user_added_to_correct_company_success(self):
        """Users who register with the same MCO should be part of the same Company"""
        rv = self.register("company_name", "first_name", "last_name", 
                        "address1", "city", "IL", "postal_code",
                        "mco", "email1@email.com", "phone_number", "password", 
                        "password", "broker")

        rv = self.register("company_name", "first_name", "last_name", 
                        "address1", "city", "IL", "postal_code",
                        "mco", "email2@email.com", "phone_number", "password", 
                        "password", "broker")

        user1 = User.query.filter_by(email='email1@email.com').first()
        user2 = User.query.filter_by(email='email2@email.com').first()
        self.assertTrue(user1.company == user2.company)
 
 
 
if __name__ == '__main__':
    unittest.main()