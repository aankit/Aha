import aha
import os

while True:
    for filename in aha.get_staged_files():
        print filename
        matches = aha.get_db_matches(filename)
        print matches
        for match in matches:
            demo_path = '/var/www/Aha/media/demo'
            # demo_filename = demo_path + '/' + aha.remove_path(filename)
            aha.cut_file(demo_path, filename, match)
            aha.make_thumbnail(demo_path)
            aha.transcode(demo_path)
        os.remove(filename)
