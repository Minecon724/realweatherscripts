import requests, zipfile, csv
from socket import inet_pton, AF_INET, AF_INET6
from tqdm import tqdm
from gzip import GzipFile
from time import time
from datetime import datetime
import shutil
from tempfile import TemporaryDirectory
from os import environ

version = int(1).to_bytes(1, 'big')
api_key = environ.get("MAXMIND_KEY")

url = f"https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City-CSV&license_key={api_key}&suffix=zip"

workdir = TemporaryDirectory()

print("downloading...")
file = open(workdir.name + "/data.zip", 'wb')
resp = requests.get(url)
date = datetime.strptime(resp.headers['last-modified'], '%a, %d %b %Y %H:%M:%S %Z')
file.write(resp.content)

print("extracting...")

with zipfile.ZipFile(workdir.name + "/data.zip", 'r') as archive:
	ipv4_blocks = ""
	ipv6_blocks = ""
	
	for i in archive.namelist():
		if i.endswith("GeoLite2-City-Blocks-IPv4.csv"):
			ipv4_blocks = i
		elif i.endswith("GeoLite2-City-Blocks-IPv6.csv"):
			ipv6_blocks = i
			
	archive.extractall(workdir.name + "/ext")
	
ipv4_blocks = csv.reader(open(workdir.name + "/ext/" + ipv4_blocks))
ipv6_blocks = csv.reader(open(workdir.name + "/ext/" + ipv6_blocks))

def encode_time(time):
	base = 1704067200 # 2024
	offset = int((time - base) / 60 / 10)
	return offset

def conversion(line, ipv6):
	
	ip, subnet = line[0].split('/')
	try:
		latitude = int(float(line[7]) * 10000) # its always 4 decimal places
		longitude = int(float(line[8]) * 10000)
	except ValueError: # geolocation missing
		latitude, longitude = (0, 0)
	#print(latitude, longitude)
	
	
	ip = inet_pton(AF_INET6 if ipv6 else AF_INET, ip)
	latitude = (latitude + 900000).to_bytes(3, 'big')
	longitude = (longitude + 1800000).to_bytes(3, 'big')
	
	out.write(ip)
	out.write(latitude)
	out.write(longitude)

timestamp = encode_time(date.timestamp()).to_bytes(2, 'big')

print("compiling ipv4...")

out = GzipFile('ipv4.geo.gz', 'wb')

out.write(version)
out.write(timestamp)
for line in tqdm(ipv4_blocks):
	if line[0] == 'network': continue
	conversion(line, False)

print("compiling ipv6...")

out.close()
out = GzipFile('ipv6.geo.gz', 'wb')

out.write(version)
out.write(timestamp)
for line in tqdm(ipv6_blocks):
	if line[0] == 'network': continue
	conversion(line, True)
	
print('cleaning...')

out.close()
workdir.cleanup()

print('done')

#file.close()
