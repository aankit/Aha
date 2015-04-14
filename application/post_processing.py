from application.models import *

found_markers = {}

videos = db.session.query(Video).all()

for video in videos:
    m = db.session.query(Marker).filter(Marker.video_id == video.id).all()
    found_markers[video.id] = []
    for fm in m:
        found_markers[video.id].append(fm)
