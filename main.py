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

            handle = lt.add_magnet_uri(ses, link, params)
            ses.start_dht()

            print ('Downloading Metadata...')
            ref.child(key).update({"Status":'Downloading Metadata...'})
            while (not handle.has_metadata()):
                time.sleep(1)
            ref.child(key).update({"Status":'Got Metadata, Starting Torrent Download...'})

            ref.child(key).update({"Status":"Starting " + handle.name()})
            print("Starting ", handle.name())

            ref.child(key).update({"Status":"Downloading  " + handle.name()})
            while (handle.status().state != lt.torrent_status.seeding):
                s = handle.status()
                state_str = ['queued', 'checking', 'downloading metadata', \
                        'downloading', 'finished', 'seeding', 'allocating']
                print ('%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s ' % \
                        (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                        s.num_peers, state_str[s.state]))
                print('Progress: %.2f%%' % (s.progress * 100))
                ref.child(key).update({"Reserve":'Progress: %.2f%%' % (s.progress * 100)})
                time.sleep(15)

            ref.child(key).update({"Status":'COMPLETE'})
            ref.child(key).update({"Status Code":2})
            print(handle.name(), "COMPLETE")
    time.sleep(15)