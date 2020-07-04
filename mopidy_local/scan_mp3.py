import logging
import pathlib
import sys

from mopidy.audio import scan
from mopidy.internal.gi import Gst
import mutagen.mp3

logger = logging.getLogger(__name__)


def parse_ufid(ufid):
    return ufid.data.decode() if ufid else None


def scan_mp3(absolute_path):
    mp3 = mutagen.mp3.MP3(absolute_path)

    def get_tag_value(keys):
        for key in keys:
            val = mp3.tags.get(key)
            if val:
                return val
        logger.debug(f"{absolute_path}: Found no value for {keys}")
        return None

    def get_tag_text_value(keys):
        val = get_tag_value(keys)
        return val.text if val else None

    def get_m_of_n(keys):
        val = get_tag_value(keys)
        if not val:
            return None, None
        m_of_n = val.text[0]
        try:
            if '/' in m_of_n:
                m, n = m_of_n.split('/', 1)
                m = int(m)
                n = int(n)
                return m, n
            else:
                m = int(m_of_n)
                return m, None
        except ValueError:
            return None, None

    def get_image_tag_value():
        val = mp3.tags.get('APIC:')
        return val.data if val else None

    # Note that this is tightly coupled to mopidy/audio/tags.py convert_tags_to_track()

    mp3_tags = {}

    def add_tag_mapping(key, value):
        if value:
            if not isinstance(value, list):
                value = [value]
            if value[0]:
                mp3_tags[key] = value

    add_tag_mapping(Gst.TAG_COMPOSER, get_tag_text_value(['TCOM']))
    add_tag_mapping(Gst.TAG_ARTIST, get_tag_text_value(['TPE1', 'TPE2']))
    add_tag_mapping(Gst.TAG_GENRE, get_tag_text_value(['TCON']))
    add_tag_mapping(Gst.TAG_TITLE, get_tag_text_value(['TIT2']))
    add_tag_mapping(Gst.TAG_BITRATE, mp3.info.bitrate)
    add_tag_mapping(Gst.TAG_ALBUM, get_tag_text_value(['TALB']))
    add_tag_mapping(Gst.TAG_ALBUM_ARTIST, get_tag_text_value(['TPE2']))
    add_tag_mapping(Gst.TAG_TRACK_NUMBER, get_m_of_n(['TRCK'])[0])
    add_tag_mapping(Gst.TAG_TRACK_COUNT, get_m_of_n(['TRCK'])[1])
    add_tag_mapping(Gst.TAG_ALBUM_VOLUME_NUMBER, get_m_of_n(['TPOS'])[0])
    add_tag_mapping(Gst.TAG_ALBUM_VOLUME_COUNT, get_m_of_n(['TPOS'])[1])
    add_tag_mapping("musicbrainz-albumid", get_tag_text_value(['TXXX:MusicBrainz Album Id']))
    add_tag_mapping("musicbrainz-artistid", get_tag_text_value(['TXXX:MusicBrainz Artist Id']))
    add_tag_mapping("musicbrainz-albumartistid", get_tag_text_value(['TXXX:MusicBrainz Album Artist Id']))
    add_tag_mapping("musicbrainz-trackid", parse_ufid(mp3.tags.get('UFID:http://musicbrainz.org'))
                    or get_tag_text_value(['TXXX:MusicBrainz Release Track Id']))
    add_tag_mapping(Gst.TAG_DATE, str(get_tag_value(['TDRL', 'TDOR', 'TYER', 'TDRC'])))
    add_tag_mapping(Gst.TAG_IMAGE, get_image_tag_value())

    result = scan._Result(uri=absolute_path.as_uri(),
                          tags=mp3_tags,
                          duration=int(1000 * mp3.info.length),
                          seekable=True,  # TODO: Is this always true for mp3s?
                          mime=mp3.mime,  # TODO: Is this a type match for mutagen.audio.scan?
                          playable=not mp3.info.sketchy)
    return result


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        result = scan_mp3(pathlib.Path(filename))
        print(filename)
        print('  tags:')
        for k, v in sorted(result.tags.items()):
            v=str(v)
            if len(v) > 40:
                v = v[:40] + '...'
            print(f'    {k}={v}')
        print(f'duration={result.duration}')
        print(f'seekable={result.seekable}')
        print(f'mime={result.mime}')
        print(f'playable{result.playable}')
