from glob import glob
from zipfile import ZipFile

filenames = glob('fetch_nyiso_load/*.zip')

for filename in filenames:
    with ZipFile(filename, 'r') as file:
        file.extractall('unpack_nyiso_load')
