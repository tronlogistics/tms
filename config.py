# -*- coding: utf8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'eat-sleep-rave-dad-IDGAFOS'


if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
                               '?check_same_thread=False')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
WHOOSH_BASE = os.path.join(basedir, 'search.db')

# Whoosh does not work on Heroku
WHOOSH_ENABLED = os.environ.get('HEROKU') is None

# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

# email server
MAIL_SERVER = 'mail.tronlogistics.com'  # your mailserver
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'admin@tronlogistics.com'
MAIL_PASSWORD = 'Tr0nadmin'

# available languages
LANGUAGES = {
    'en': 'English',
    'es': 'Español'
}

CORS_HEADERS = 'Content-Type'

# microsoft translation service
MS_TRANSLATOR_CLIENT_ID = ''  # enter your MS translator app id here
MS_TRANSLATOR_CLIENT_SECRET = ''  # enter your MS translator app secret here

# administrator list
ADMINS = ['admin@tronlogistics.com', 'john@tronlogistics.com', 'troy@tronlogistics.com']

# pagination
POSTS_PER_PAGE = 50
MAX_SEARCH_RESULTS = 50
