DEBUG = True
SECRET_KEY = 'newkey'  # make sure to change this
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://aha:aha@/aha'  # 'sqlite:///test.db'
WTF_CSRF_ENABLED = True
LOG_FILE = '/var/www/Aha/application.log'
MEDIA_DIR = '/var/www/Aha/media'
