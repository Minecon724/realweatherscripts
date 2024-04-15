from hashlib import sha256

def hash():
    for fn in ['ipv4.geo.gz', 'ipv6.geo.gz']:
        f = open(fn, 'rb')

        hasher = sha256()
        hasher.update(f.read())
        digest = hasher.digest()

        out = open(fn + '.sha256', 'wb')
        out.write(digest)

        out.close()
        f.close()