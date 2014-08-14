#! /usr/bin/env python3

import sys, os, os.path, importlib, tempfile
import docformats, doctypes
from argparse import ArgumentParser

class UnknownDocFormat(BaseException):
  pass

AVAILABLE_DOC_TYPES = ['sdoc']
ZEAL_DOCSET_DIR = "~/.local/share/zeal/docsets"
# TODO: other formats

def load_format_module(name):
  return importlib.import_module('docformats.%s' % name)

def load_type_module(name):
  return importlib.import_module('doctypes.%s' % name)

def detect_doc_format(directory):
  for format in AVAILABLE_DOC_TYPES:
    module = load_type_module(format)
    detected = module.detect(directory)
    if detected:
      return format
  raise UnknownDocFormat()

def build_docset(options):
  dir = options['directory']
  tp = load_type_module(options['type'])
  fm = load_format_module(options['format'])
  with tempfile.TemporaryDirectory() as tmpdir:
    fm.create_structure(tmpdir)
    manifest = tp.get_manifest(dir)
    fm.build_manifest(tmpdir, manifest)
    fm.create_index(tmpdir, tp.build_index(dir))
    fm.copy_files(tmpdir, dir, tp.get_doc_files(dir))
    fm.package(tmpdir, options['output'], manifest['bundle_identifier'])

def parse_options(argv):
  parser = ArgumentParser(description='Generate Zeal/Dash docset from already built documentation.',
                          epilog='Currently supported types: %s' % ','.join(AVAILABLE_DOC_TYPES))
  parser.add_argument('directory', type=str, nargs='?', metavar='dir', default='.', help='Path to project')
  parser.add_argument('-t', '--type', type=str, choices=AVAILABLE_DOC_TYPES, default='autodetect', metavar='TYPE', help='Documentation format')
  parser.add_argument('--dash', action='store_const', const='dash', dest='format', help='Build Dash docset package')
  parser.add_argument('--zeal', action='store_const', const='zeal', dest='format', help='Build Zeal docset directory')
  parser.add_argument('--install', action='store_const', dest='output', const=ZEAL_DOCSET_DIR, help="When building Zeal docsets, try to install them in Zeal's default docset directory (%s)" % ZEAL_DOCSET_DIR)
  parser.add_argument('-o', '--output', dest='output', metavar='DEST', help='Build output in DEST, instead of current directory or Zeal docset directory')
  parser.set_defaults(format='zeal', output='.')
  return parser.parse_args(argv)

def main():
  options = parse_options(sys.argv[1:])
  if options.type == 'autodetect':
    try:
      options.type = detect_doc_format(options.directory)
    except UnknownDocFormat:
      print('Error: Unknown documentation format. Supported ones are: %s' % ','.join(AVAILABLE_DOC_TYPES))
      sys.exit(1)
  build_docset(vars(options))

if __name__ == "__main__":
  main()
