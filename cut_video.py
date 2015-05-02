import os
import aha

for filename in aha.get_staged_files():
    matches = aha.get_db_matches(filename)
    for match in matches:
        media_path = aha.make_media_path(filename, match)
        media_filename = media_path + '/' + aha.remove_path(filename)
        if not os.path.isfile(media_filename):
            aha.cut_file(media_path, filename, match)
    if aha.check_purge_state(filename) is True:
        os.remove(filename)
        print "removed %s" % (filename)
