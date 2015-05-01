import aha
import os

for filename in aha.get_staged_files():
    matches = aha.get_file_matches(filename)
    for match in matches:
        media_path = aha.get_media_path(filename, match)
        start, duration = aha.get_relative_cut(filename, match)
        aha.cut_file(filename, media_path, start, duration)
    if aha.check_purge_status(filename):
        os.remove(filename)
        print "removed %s" % (filename)
