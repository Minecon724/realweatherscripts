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

def encode_time(time):
	base = 1704067200 # 2024
	offset = int((time - base) / 60 / 10)
	return offset

def conversion(line, ipv6, out):
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

def compile(ipv6: bool, blocks, timestamp):
	print("compiling", "ipv6" if ipv6 else "ipv4")

	out = GzipFile('ipv4.geo.gz', 'wb')

	out.write(version)
	out.write(timestamp)
	for line in tqdm(blocks):
		if line[0] == 'network': continue
		conversion(line, ipv6, out)

	out.close()

def run(api_key: str):
	url = f"https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City-CSV&license_key={api_key}&suffix=zip"
	workdir = TemporaryDirectory()

	print("downloading...")
	file = open(workdir.name + "/data.zip", 'wb')
	resp = requests.get(url)
	date = datetime.strptime(resp.headers['last-modified'], '%a, %d %b %Y %H:%M:%S %Z')
	file.write(resp.content)
	file.close()

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

	timestamp = encode_time(date.timestamp()).to_bytes(2, 'big')

	compile(False, ipv4_blocks, timestamp)
	compile(True, ipv6_blocks, timestamp)

	workdir.cleanup()

	print('done')