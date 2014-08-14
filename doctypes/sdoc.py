__all__ = ['detect', 'get_manifest', 'build_index', 'get_doc_files']

import os.path, glob, re, subprocess, json, tempfile, glob
from itertools import chain
import code

def detect(dir):
  docdir = os.path.join(dir, 'doc')
  names = ['files', 'classes', 'panel', 'js']
  if not all(os.path.exists(os.path.join(docdir, name)) for name in names):
    return False
  if not os.path.exists(os.path.join(docdir, 'js', 'search_index.js')):
    return False
  return True

def load_manifest_from_gemspec(filename):
  # Use Ruby to do heavy lifting! Assume a modern installation,
  # at least with RubyGems.
  ruby_script = """
  require 'rubygems'
  require 'json'
  gem = Gem::Specification.load('%s')
  spec = {name: gem.name, version: gem.version} # Add more when needed
  puts spec.to_json
  """ % filename
  gem_data = None
  with tempfile.TemporaryFile(mode='w',encoding='utf-8') as ruby_script_file:
    ruby_script_file.write(ruby_script)
    ruby_script_file.flush()
    ruby_script_file.seek(0)
    gem_data = json.loads(subprocess.check_output('ruby', stdin=ruby_script_file).decode('utf-8'))

  return dict(
    bundle_identifier = '%(name)s_%(version)s' % gem_data,
    bundle_name = gem_data['name'],
    family = gem_data['name']
  )

def get_manifest(dir):
  gemspec = glob.glob(os.path.join(dir, '*.gemspec'))
  manifest = None
  if len(gemspec) > 0:
    # handle errors here
    manifest = load_manifest_from_gemspec(gemspec[0])

  if not manifest:
    projname = os.path.basename(dir)
    manifest = dict(
      bundle_identifier = projname,
      bundle_name = projname
    )

  return manifest

def index_entry(row):
  # TODO: how to tell classes, methods, modules, constants apart?
  return dict(name=row[0], path=row[2])

def build_index(root):
  filename = os.path.join(root, 'doc/js/search_index.js')

  with open(filename) as fp:
    fp.seek(18) # var search_data = 
    search_data = json.load(fp)
    index = search_data['index']
    return (index_entry(row) for row in index['info'])

def get_doc_files(root):
  join = lambda *paths: os.path.join(root, 'doc', *paths)
  return chain(
    glob.glob(join('classes', '**', '*.html')),
    glob.glob(join('files', '**', '*.html')),
    glob.glob(join('css', '*.css'))
  )
