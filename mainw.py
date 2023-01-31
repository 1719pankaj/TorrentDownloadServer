import firebase_admin as fa
from firebase_admin import db
import json

import libtorrent as lt
import time
import datetime

time.sleep(5)

databaseURL = 'https://torrentbotserver-default-rtdb.asia-southeast1.firebasedatabase.app/'

cred_obj = fa.credentials.Certificate('admin_key_fb.json')
default_app = fa.initialize_app(cred_obj, {'databaseURL':databaseURL})

ref = db.reference("/Torrents/")

while True:
    raw = json.dumps(ref.get())
    data = json.loads(raw)
    link = ""

    ses = lt.session()
    ses.listen_on(6881, 6891)
    params = {
        'save_path': '/',
        'storage_mode': lt.storage_mode_t(2),
        }


    for key, value in data.items():
        if value["Status Code"] ==  0 and value["Magnet"] != "nil":
            link = value["Magnet"]
            ref.child(key).update({"Status Code":1})
            
            ref.child(key).update({"Status":"Downloading..."})
            from torrentp import TorrentDownloader
            torrent_file = TorrentDownloader(link, '/')
            torrent_file.start_download()

            ref.child(key).update({"Status":'COMPLETE'})
            ref.child(key).update({"Status Code":2})
            print("COMPLETE")
    time.sleep(15)