import aha

while True:
    for media_path, db_duration in aha.get_media_paths():
        gap_total, num_files = aha.check_consecutive(media_path)
        video_duration = aha.check_duration(media_path)
        duration_diff = db_duration - video_duration
        print "this is the gap total: %d" % (gap_total)
        if gap_total < 4 * num_files:
            print "concatenating %s" % (media_path)
            if aha.build_ready(media_path) and aha.new_file_exists(media_path):
                aha.sort_concat_file(media_path)
                aha.concatenate(media_path)
                aha.make_thumbnail(media_path)
        else:
            print gap_total

        if duration_diff <= 10:
            print "cleaning %s" % (media_path)
            aha.clean_build_media(media_path)
        else:
            print duration_diff
