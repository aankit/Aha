DEBUG = True
SECRET_KEY = 'newkey'  # make sure to change this
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://aha:aha@/aha'  # 'sqlite:///test.db'
WTF_CSRF_ENABLED = True
APPLICATION_DIR = '/var/www/Aha'
MEDIA_DIR = APPLICATION_DIR+'/media'
STAGING_DIR = MEDIA_DIR+'/staging'
LOG_FILE = 'application.log'
