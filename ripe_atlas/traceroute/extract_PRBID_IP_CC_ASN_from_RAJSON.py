#!/usr/bin/env python3
# by Quirin Scheitle -- scheitle@net.in.tum.de
import json
import sys
from multiprocessing.dummy import Pool as ThreadPool
from ripe.atlas.cousteau import Probe


def probe_to_cc_asn(idin):
    probe = Probe(id=idin)
    cc, asn = probe.country_code, probe.asn_v4
    sys.stdout.write('.') # for progress indication
    sys.stdout.flush()
    return idin, cc, asn


def parse_scamper_json(filename):
    if not filename:
        raise NameError('ERROR: inputs missing at parse_ripeatlas:', filename)

    probe_ids = dict()
    with open(filename) as f:
        for line in f:
            try:
                data = json.loads(line)
            except json.decoder.JSONDecodeError as e:
                print("json decoder error: ", e, line)
                sys.exit(1)
            probe_ids[data["prb_id"]] = data["from"]

    print("Writing output from {} probes to: {}".format(len(probe_ids), filename + ".prbid_ip_cc_asn"))
    with open(filename + ".prbid_ip_cc_asn", 'w') as fout:
        fout.write("prb_id, IP, CC, ASN\n")
        ids = list(probe_ids.keys())
        pool = ThreadPool(200)
        results = pool.map(probe_to_cc_asn, ids)
        pool.close()
        pool.join()
        for i in results:
            prbid = i[0]
            cc = i[1]
            asn = i[2]
            ip = probe_ids[prbid]
            fout.write("{},{},{},{}\n".format(prbid, ip, cc, asn))
    return


if __name__ == "__main__":
    if len(sys.argv) == 2:
        parse_scamper_json(sys.argv[1])
    else:
        print("CRITICAL: filename of RA trace as json needs to be argument")
