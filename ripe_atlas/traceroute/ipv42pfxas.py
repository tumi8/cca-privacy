#!/usr/bin/env python3

import ipaddress
import sys
import pickle
import time

def readpfxfile(prefix_fname):
    prefixes = list()
    time_before = time.time()
    try:
        pklfile = open(prefix_fname+".pickle",'rb')
        prefixes = pickle.load(pklfile)
        pklfile.close()
        print("pickle loaded after: " , str(time.time()-time_before) )
        return prefixes;
    except FileNotFoundError as e:
        print("FileNotFoundError :", e, "reading from raw data and creating pickle")
        fh = open(prefix_fname)
        for line in fh.readlines():
            prefixes.append(line.strip())
        fh.close()
        print("pfxes read after: " + str(time.time()-time_before))
        pklfile=open(prefix_fname+".pickle",'wb')
        pickle.dump(prefixes,pklfile)
        print("pickle dumped after: " + str(time.time()-time_before))
        pklfile.close()
        return prefixes

def main():
    ip_fname = sys.argv[1]
    prefix_fname = sys.argv[2]
    prefixes = readpfxfile(prefix_fname)

    fh2 = open(ip_fname + ".aspfx.csv", 'w')
    with open(ip_fname) as fh:
        for line in fh.readlines():
            ip = line.strip()
            res = prefix_lookup(ip, prefixes)
            fh2.write(ip + "," + res[0] + "/" + res[1] + "," + res[2] + "\n")
    fh2.close


def prefix_lookup_merged(ipin, prefixes):
    """ returns ['8.8.8.0/24','15169']"""
    a, b, c = prefix_lookup(ipin, prefixes)
    return ["{}/{}".format(a, c), c]


def prefix_lookup(ipin, prefixes):
    """ returns ['8.8.8.0', '24', '15169'] """
    ip = ""
    if not isinstance(ip, str):
        ip = str(ipin)
    elif (isinstance(ipin, ipaddress.IPv4Address)):
        ip = str(ipin)
    else:
        ip = ipin

    # first find starting /8 prefix entry, they are sorted numerically -> binary search on /8
    num_prefixes = len(prefixes)
    curr = int(num_prefixes / 2)
    step = int(num_prefixes / 2)
    correct = -1

    ip_slash8 = int(ip.split(".")[0])

    one = False

    while True:
        pfx_ip = prefixes[curr].split("\t")[0]
        # First byte -> /8
        if int(pfx_ip.split(".")[0]) == ip_slash8:
            if correct == -1 or curr < correct:
                correct = curr
            curr = curr - step
        elif int(pfx_ip.split(".")[0]) > ip_slash8:
            curr = curr - step
        elif int(pfx_ip.split(".")[0]) < ip_slash8:
            curr = curr + step

        curr = min(curr, len(prefixes) - 1)

        if step == 1:
            if one:
                break
            one = True
        else:
            step = int(step / 2)

    curr = correct
    candidate = ipaddress.IPv4Network(prefixes[correct].split("\t")[0].split(".")[0] + ".0.0.0/8")

    ipa = ipaddress.IPv4Address(ip)

    while True:
        ip_network, pfx_network, _ = prefixes[curr].split("\t")
        network = ipaddress.IPv4Network(ip_network + "/" + pfx_network)
        # If this network does not overlap with the last candidate network
        if not network.overlaps(candidate):
            break
        # We want the most specific prefix
        elif int(pfx_network) < candidate.prefixlen:
            pass
        elif ipa in network:
            correct = curr
            candidate = ipaddress.IPv4Network(prefixes[correct].split("\t")[0] + "/" + prefixes[correct].split("\t")[1])

        curr += 1

    ip_network, pfx_network, _ = prefixes[correct].split("\t")
    network = ipaddress.IPv4Network(ip_network + "/" + pfx_network)
    if ipa in network:
        res = prefixes[correct].split("\t")
    else:
        res = ["0.0.0.0", "0", "0"]
    # print(ip + "," + res[0] + "," + res[1] + "," + res[2])
    # res: prefix, prefix length, asn
    return res


if __name__ == "__main__":
    main()
