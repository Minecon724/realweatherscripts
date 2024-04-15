from ftplib import FTP
import requests
from os import listdir
from io import BytesIO

def upload(server, user, password):
    ftp = FTP(server)
    ftp.login(user, password)

    for f in [i for i in listdir() if i.endswith('.geo.gz')]:

        # 1. Minify the index.html file using minify-html
        file = open(f, 'rb')

        # 2. Upload the file to an FTP server

        ftp.storbinary('STOR ' + f, file)
        print("uploaded", f)

    # Quit ftp

    ftp.quit()

    print("done")