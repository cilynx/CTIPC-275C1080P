#!/usr/bin/python3

header = b'hxVF'
salt = b'IPCAM'
salt_offset = 0x1d # shadow bin
salt_offset = 0x1c # most of the time
payload_offset = 0x110

url = 'http://192.168.1.88/web/cgi-bin/hi3510/restore.cgi' # when cam is AP
url = 'http://ipcam/web/cgi-bin/hi3510/restore.cgi' # when cam is client on your network
import requests

import sys

from time import sleep

from struct import *
import hashlib
m = hashlib.md5()

magic_byte = 0x99 # config_backup.bin
magic_byte = 0xb4 # config_backup-on_garagenet.bin
magic_byte = int(sys.argv[1]) # read magic_byte from command line

import shelve

db = shelve.open('magic_bytes')
if str(magic_byte) in db:
    print(hex(magic_byte), db[str(magic_byte)])
    db.close()
    exit()

with open("archive.tgz", "rb") as archive:
    payload = archive.read()
    bytes = payload + salt
    m.update(bytes)
    checksum = str.encode(m.hexdigest())

with open("output.bin", "wb") as binfile:
    binfile.write(pack('>4sh18xBB2x5s195x32s252x', header, payload_offset, magic_byte, salt_offset, salt, checksum))
    binfile.write(payload)

print(hex(magic_byte))

with open("output.bin", "rb") as output:
    try:
        r = requests.post(url, files={'config_backup.bin': output}, auth=requests.auth.HTTPBasicAuth('admin','admin'), timeout=60)
        print(r.text)
        db[str(magic_byte)] = r.text
    except:
        print("timeout")

db.close()
