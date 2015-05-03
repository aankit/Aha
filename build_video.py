import aha

while True:
    for media_path, db_duration in aha.get_media_paths():
        #right now this is stats
        gap_total, num_files = aha.check_consecutive(media_path)
        video_duration = aha.check_duration(media_path)
        duration_diff = db_duration - video_duration
        if aha.build_ready(media_path) and aha.new_file_exists(media_path):
            #print "concatenating %s" % (media_path)
            aha.sort_concat_file(media_path)
            aha.concatenate(media_path)
            aha.make_thumbnail(media_path)
        if duration_diff <= 15:
            #print "cleaning %s" % (media_path)
            aha.clean_build_media(media_path)
        #else:
            #print duration_diff
