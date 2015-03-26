import os
from application import app
from application import scheduler

def runserver():
	scheduler.start()
	print 'scheduler started'
	port = int(os.environ.get('PORT', 3000))
	app.run('0.0.0.0', port=port)

if __name__ == '__main__':
	runserver()