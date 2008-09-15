import glob
import mimetypes
import os.path
import shutil
import sys
import urlparse
import xml.etree.ElementTree as ET

import pkg_resources

import markdown
import mutagen
import mutagen.easyid3
import mutagen.id3
import web

header_fn = 'README'
if os.path.exists(header_fn):
    header = file(header_fn).read()
else:
    header = None

files = sorted(glob.glob('*.mp3'))
render = web.template.render(pkg_resources.resource_filename(__name__, 'templates/'))
web.template.Template.globals['markdown'] = markdown.markdown

class TrackInfo:
    def __init__(self, filename):
        try:
            self.load(filename)
        except mutagen.id3.error:
            self.artist = "No Artist"
            self.title = "No Title"
            self.duration = "?:??"

    def load(self, filename):
        short_tags = full_tags = mutagen.File(filename)

        if isinstance(full_tags, mutagen.mp3.MP3):
            short_tags = mutagen.easyid3.EasyID3(filename)

        self.artist = short_tags['artist'][0]
        self.title = short_tags['title'][0]
        self.duration = "%u:%.2d" % (full_tags.info.length / 60, full_tags.info.length % 60)

def tracklist(url_root = ''):
    for count, fn in enumerate(files):
        info = TrackInfo(fn)
        url = urlparse.urljoin(url_root,
                               web.net.urlquote(web.http.url(fn)))

        yield count, info, url

def cgi_tracklist():
    return tracklist(web.ctx.homedomain)

class XSPF:
    def GET(self):
        web.header('Content-Type', 'application/xspf+xml')
        print render.xspf(cgi_tracklist())

class Index:
    def GET(self):
        print render.index(header, cgi_tracklist())

class Static:
    def leak_file(self, f):
        while True:
            buf = f.read(16 * 1024)
            if not buf:
                break
            yield buf
        f.close()

    def GET(self, filename):
        content_type, encoding = mimetypes.guess_type(filename)
        web.header('Content-Type', content_type)

        # Serve the music.
        if filename in files:
            return self.leak_file(file(filename))

        # Serve the necessities.
        fn_static = os.path.join('static', filename)

        if pkg_resources.resource_exists(__name__, fn_static):
            f = pkg_resources.resource_stream(__name__, fn_static)
            return self.leak_file(f)

        # Give up.
        return web.notfound()

def cgi():
    urls = ('/xspf', 'XSPF',
            '/', 'Index',
            '/(.*)', 'Static',)
    web.run(urls, globals())

def static():
    # Generate the templates. (xspf, index)
    templates = {'xspf': render.xspf(tracklist()),
                 'index.html': render.index(header, tracklist())}

    for fn, data in templates.items():
        f = file(fn, 'w')
        f.write(data)
        f.close()

    # Copy all the static files.
    for fn in pkg_resources.resource_listdir(__name__, 'static'):
        resource_fn = os.path.join('static', fn)
        resource = pkg_resources.resource_filename(__name__, resource_fn)
        shutil.copy(resource, fn)
