import aha
import os

for filename in aha.get_staged_files():
    matches = aha.get_file_matches(filename)
    for match in matches:
        media_path = aha.get_media_path(filename, match)
        media_filename = media_path + '/' + aha.remove_path(filename)
        if not os.path.isfile(media_filename):
            aha.cut_file(filename, match)
    if aha.check_purge_state(filename):
        os.remove(filename)
        print "removed %s" % (filename)
