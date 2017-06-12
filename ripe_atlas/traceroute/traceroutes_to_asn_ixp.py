#!/usr/local/bin/python3

# parses ATLAS traceroutes into AS/IXP format and evaluates it
# usage: script.py atlas.json ixp-db.csv ip-as-file

# load IXP data
import sys
import csv
import ipaddress
ixps = sys.argv[2]
pfx2ixp = dict()
# format: 0-1, 1-OptIX-LA, 2-Not an exchange, 3-IPv4, 4-Unicast, 5-Unknown, 6-200.61.194.0/24, 0
# columns of interest: 1,6
with open(ixps, 'r', encoding='utf-8') as ixpfile:
	ixpr = csv.reader(ixpfile, delimiter=',')
	for row in ixpr:
		# print(row[1],row[6])
		try:
			nw = ipaddress.IPv4Network(row[6].strip())
			pfx2ixp[nw] = row[1].strip()
		except ipaddress.AddressValueError as e:
			pass
		except ValueError as e:
			print("Error: " + str(e))

try:
	del nw, row  # just to avoid mistakes by accidentally using these
except:
	pass
print("Imported IXP data, size of pfx2ixp dict: {}".format(len(pfx2ixp)))
sys.stderr.write("Imported IXP data, size of pfx2ixp dict: {} \n".format(len(pfx2ixp)))


# load AS data using iputils code
import ipv42pfxas
prefix_fname = sys.argv[3]
prefixes = list()

fh = open(prefix_fname)
for line in fh.readlines():
	prefixes.append(line.strip())
fh.close()

print("Imported pfx2as data, size of prefixes: {}".format(len(prefixes)))
sys.stderr.write("Imported pfx2as data, size of prefixes: {} \n".format(len(prefixes)))

# src: iana-special
prefixes_bogon_list = [
	"0.0.0.0	8	-",
	"10.0.0.0	8	-",
	"100.64.0.0	10	-",
	"127.0.0.0	8	-",
	"169.254.0.0	16	-",
	"172.16.0.0	12	-",
	"192.0.0.0	24	-",
	"192.0.2.0	24	-",
	"192.88.99.0	24	-",
	"192.168.0.0	16	-",
	"198.18.0.0	15	-",
	"198.51.100.0	24	-",
	"203.0.113.0	24	-",
	"240.0.0.0	4	-",
	"255.255.255.255	32	-",
	"224.0.0.0	4	-"
]
prefixes_bogon = list()
for line in prefixes_bogon_list:
	prefixes_bogon.append(line.strip())

a = ipv42pfxas.prefix_lookup("198.51.100.0", prefixes_bogon)
assert a == ['198.51.100.0', '24', '-']
a = ipv42pfxas.prefix_lookup("8.8.8.8", prefixes_bogon)
assert a == ['0.0.0.0', '0', '0']

# small unit test to check that pfx2as works
a = ipv42pfxas.prefix_lookup("17.0.98.68", prefixes)
assert a == ['17.0.64.0', '18', '714']
a = ipv42pfxas.prefix_lookup("250.0.0.0", prefixes)
assert a == ['0.0.0.0', '0', '0']

from ripe.atlas.sagan import Result
import sys
file = sys.argv[1]
file2 = open(file + ".ip-mappings", 'w')
ipm = dict()
d = dict()
count_traces = 0
import time
start_time = time.time()
with open(file) as results:
	for result in results.readlines():
		parsed_result = Result.get(result)
		count_traces = count_traces + 1
		if count_traces % 100 == 0:
			sys.stderr.write("{} traces processed after {} seconds. \n".format(
				count_traces, round(time.time() - start_time, 1)))
		#  if(count_traces > 20):
		#  break
		try:
			for i in parsed_result.hops:
				if i.packets[0].origin is not None:
					try:
						ipa = ipaddress.IPv4Network(i.packets[0].origin)
					except Exception as e:
						print("Parsing Error: " + str(e))
					traceid = str(parsed_result.measurement_id) + "_" + str(parsed_result.probe_id)
					# check if IP cached from earlier lookup
					if ipa in ipm:
						k = ipm[ipa]
						if k != "-":
							d[k][traceid] = 1
						#  print("reading IP {} from cache as {}, adding traceid {}".format(ipa, ipm[ipa], traceid))
					else:
						# first match IXP
						ixpmatch = 0
						for ixpnw, ixpname in pfx2ixp.items():
							if ixpnw.overlaps(ipa):
								k = "IXP-" + ixpname
								if k not in d:
									d[k] = dict()
								d[k][traceid] = 1
								ipm[ipa] = k
								ixpmatch = 1
								#  print("IXPmatch: {}, {},{}".format(ipa, ixpname, traceid))
								break
						# if not IXP, search AS
						if ixpmatch is 0:
							# check whether IP is iana-special and should not be mapped to AS
							[_, _, asnhlp] = ipv42pfxas.prefix_lookup(ipa.network_address, prefixes_bogon)
							if asnhlp == "-":
								asn = 0
							else:
								[nw, pfx, asn] = ipv42pfxas.prefix_lookup(ipa.network_address, prefixes)
							if int(asn) > 0:
								k = "AS-" + asn
								#  print("AS:", k, nw, ipa)
								if k not in d:
									d[k] = dict()
								d[k][traceid] = 1
								ipm[ipa] = k
							else:
								#  no match for AS or IXP
								print("No IXP/AS match: " + str(ipa))
								ipm[ipa] = "-"
								pass
		except Exception as e:
			print("Parsing failed for probe ID: {} with error {}".format(parsed_result.probe_id, e))
			print("parsed result: ", parsed_result.hops)
			import traceback
			traceback.print_exc(file=sys.stdout)

count = dict()
for k, v in d.items():
	count[k] = len(v)
	#  print(k,v,len(v))
	#  print(str(k) + " : " + str(len(v)))


print("Complete AS list:")
print("AS, #traces traversing AS, % traces traversing AS")
sc = sorted(count.items(), key=lambda x: x[1])
for i in sc:
	percent = 100 * i[1] / count_traces
	print("{},{},{}%".format(str(i[0]), str(i[1]), round(percent, 2)))
print("Total traces: " + str(count_traces))

print("Top 10 AS list (excluding AS-714):")
print("Rank, AS, #traces traversing AS, % traces traversing AS, CDF % traces traversing AS")
cdf = 0.0
ctr = 0
for i in reversed(sc):
	if str(i[0]) == "AS-714":  # Skip AS-714 (Apple) as all traceroutes target this AS
		continue

	ctr += 1
	percent = 100 * i[1] / count_traces
	cdf = cdf + percent
	print("#{}, {}, {}, {}%, {}%".format(ctr, str(i[0]), str(i[1]), round(percent, 2), round(cdf, 0)))
	if ctr == 10:
		break


for ip, v in ipm.items():
	file2.write(str(ip) + "," + v + "\n")
file2.close()
