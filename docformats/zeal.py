import shutil, os, os.path
from .dash import create_structure, build_manifest, create_index, copy_files

def package(root, output, name):
  dest = os.path.expanduser(os.path.join(output, '%s.docset' % name))
  src = os.path.join(root, 'Contents')
  print("copying %s to %s" % (src, dest))
  shutil.copytree(src, dest) 
