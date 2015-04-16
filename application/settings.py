DEBUG = False
SECRET_KEY = 'newkey'  # make sure to change this
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://aha:aha@/aha'  # 'sqlite:///test.db'
WTF_CSRF_ENABLED = True
VIDEO_PATH = '/home/pi/picam/rec/archive'
TMP_VIDEO_PATH = '/home/pi/picam/rec/tmp'
RECORD_PATH = '/home/pi/picam/hooks'
LOG_FILE = 'aha.log'
