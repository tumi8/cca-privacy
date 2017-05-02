#!/usr/local/bin/python3

import base64
import dns.message # provided by dnspython

## testing
#abuf='mE6BgAABAAoAAAAACTEtY291cmllcgRwdXNoBWFwcGxlA2NvbQAAAQABwAwABQABAAA2pwAlATESY291cmllci1wdXNoLWFwcGxlA2NvbQZha2FkbnMDbmV0AMA2AAUAAQAAADsAJRdwb3AtZXVyLWJlbmVsdXgtY291cmllcgpwdXNoLWFwcGxlwEvAZwABAAEAAAA7AAQR/EwVwGcAAQABAAAAOwAEEfxMGcBnAAEAAQAAADsABBH8TBfAZwABAAEAAAA7AAQR/EwRwGcAAQABAAAAOwAEEfxMI8BnAAEAAQAAADsABBH8TB/AZwABAAEAAAA7AAQR/EwKwGcAAQABAAAAOwAEEfxMEw=='
#dnsmsg = dns.message.from_wire(base64.b64decode(abuf))
#print(dnsmsg)

from ripe.atlas.sagan import Result # provided by ripe.atlas.sagan
import sys
file=sys.argv[1]
with open (file) as results:
	for result in results.readlines():
		parsed_result = Result.get(result)
		try:
			print(dns.message.from_wire(base64.b64decode(str(parsed_result.responses[0].abuf))))
		except Exception as e:
			print("Parsing failed for probe ID: " + str(parsed_result.probe_id))
			print(str(e))
