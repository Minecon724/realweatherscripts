from time import sleep, time
from os import path, environ
from datetime import datetime
import maxmind, upload, hasher

api_key = environ.get("MAXMIND_KEY")
ftp_host = environ.get("FTP_HOST")
ftp_user = environ.get("FTP_USER")
ftp_password = environ.get("FTP_PASSWORD")

while True:
    do_update = not path.exists("ipv4.geo.gz") or not path.exists("ipv6.geo.gz")
    do_update = do_update and time() - path.getmtime("ipv6.geo.gz") > 86400
    do_update = True

    if do_update:
       # maxmind.run(api_key)
        hasher.hash()
        upload.upload(ftp_host, ftp_user, ftp_password)
    else:
        print("updating in %d s" % (time() - path.getmtime("ipv6.geo.gz")))

    sleep(3600)