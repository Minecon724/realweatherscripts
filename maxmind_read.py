from gzip import GzipFile
from socket import inet_ntop, AF_INET
from datetime import datetime

ipv4_blocks = GzipFile('ipv4.geo.gz')
	
def recover_time(timestamp):
	base = 1704067200 # 2024
	return base + timestamp * 60 * 10
	
time = recover_time(int.from_bytes(ipv4_blocks.read(2), 'big'))
print(datetime.fromtimestamp(time))

while True:
	try:
		address = inet_ntop(AF_INET, ipv4_blocks.read(4))
	except:
		break
	subnet = (int.from_bytes(ipv4_blocks.read(1), 'big'))
	latitude = (int.from_bytes(ipv4_blocks.read(3), 'big') - 900000) / 10000
	longitude = (int.from_bytes(ipv4_blocks.read(3), 'big') - 1800000) / 10000

	print(address, subnet, latitude, longitude)
