import aha

while True:
    for media_path, db_duration in aha.get_media_paths():
        gaps = aha.check_consecutive(media_path)
        video_duration = aha.check_duration(media_path)
        duration_diff = db_duration - video_duration
        if gaps < 15:
            print "concatenating %s" % (media_path)
            aha.sort_concat_file(media_path)
            aha.concatenate(media_path)
            aha.make_thumbnail(media_path)
        else:
            print gaps
        if duration_diff <= 10:
            print "cleaning %s" % (media_path)
            aha.clean_build_media(media_path)
        else:
            print duration_diff
