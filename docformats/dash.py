import os, os.path, subprocess, shutil, tarfile
from lxml import etree as ET
from lxml.builder import E

import code

def create_structure(root):
  for dir in ['Contents', 'Contents/Resources', 'Contents/Resources/Documents']:
    os.mkdir(os.path.join(root, dir))

def build_manifest(root, params):
  plist = E.plist({'version':'1.0'}, 
                  E.dict(
                    E.key('CFBundleIdentifier'),
                    E.string(params['bundle_identifier']),
                    E.key('CFBundleName'),
                    E.string(params['bundle_name']),
                    E.key('DocSetPlatformFamily'),
                    E.string(params['family']),
                    E.key('isDashDocset'),
                    E.true()
                  ))

  filename = os.path.join(root, 'Contents/Info.plist')
  with open(filename, 'wb') as fp:
    fp.write(ET.tostring(plist, xml_declaration=True, pretty_print=True, encoding='utf-8'))

def build_sql(index):
  yield 'BEGIN TRANSACTION;'
  yield 'CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);'
  for i, item in enumerate(index):
    yield "INSERT INTO searchIndex VALUES (%d, '%s', '', '%s');" % (i, item['name'], item['path'])

  yield 'COMMIT;'

def create_index(root, index):
  db_filename = os.path.join(root, 'Contents/Resources', 'docSet.dsidx')
  sqlite3 = subprocess.Popen(['sqlite3', db_filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  # output not needed, sqlite will just create the dbfile
  sqlite3.communicate(bytes("\n".join(build_sql(index)), 'utf-8'))

def copy_files(dest, root, file_list):
  doc_join = lambda *args: os.path.join(dest, 'Contents/Resources/Documents', *args)
  doc_root = os.path.join(root, 'doc')
  for file in file_list:
    path = os.path.relpath(file, doc_root)
    dest_path = doc_join(path)
    # print("copying %s to %s & %s" % (file, dest_path, path))
    if not os.path.exists(os.path.dirname(dest_path)):
      os.makedirs(os.path.dirname(dest_path))
    shutil.copy(file, os.path.join(dest, dest_path))

def package(root, output, name):
  if os.path.isdir(output):
    path = os.path.join(output, '%s.tgz' % name)
  else:
    path = output

  with tarfile.open(path, 'w:gz') as tar:
    tar.add(os.path.join(root, 'Contents'), arcname='%s.docset/Contents' % name, recursive=True)
