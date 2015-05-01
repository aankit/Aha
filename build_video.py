import aha
from glob import glob

for media_path in aha.get_media_paths():
    if glob(media_path+'/*.ts'):
        aha.concatenate(media_path)
        aha.make_thumbnail()
