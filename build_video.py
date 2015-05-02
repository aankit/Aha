import aha

for media_path, db_duration in aha.get_media_paths():
    gaps = aha.check_consecutive(media_path)
    print gaps
    video_duration = aha.check_duration(media_path)
    duration_diff = db_duration - video_duration
    print duration_diff
    if gaps < 15:
        aha.sort_concat_file(media_path)
        aha.concatenate(media_path)
        aha.make_thumbnail(media_path)
    if duration_diff <= 10:
        aha.clean_build_media(media_path)
