from gzip import GzipFile
from socket import inet_ntop, AF_INET
from datetime import datetime

def recover_time(timestamp):
	base = 1704067200 # 2024
	return base + timestamp * 60 * 10
	
def load(blocks_file, ipv6):
	time = recover_time(int.from_bytes(blocks_file.read(2), 'big'))
	print(datetime.fromtimestamp(time))

	subnets = 0

	while True:
		try:
			address = inet_ntop(AF_INET, blocks_file.read(16 if ipv6 else 4))
		except:
			break
		subnet = (int.from_bytes(blocks_file.read(1), 'big'))
		latitude = (int.from_bytes(blocks_file.read(3), 'big') - 900000) / 10000
		longitude = (int.from_bytes(blocks_file.read(3), 'big') - 1800000) / 10000

		subnets += 1

	print(subnets, "subnets")

ipv4_blocks = GzipFile('ipv4.geo.gz')
ipv6_blocks = GzipFile('ipv4.geo.gz')

print("now loading ip legacy (v4)...")
load(ipv4_blocks)
print("now loading ip (v6)...")
load(ipv6_blocks)
