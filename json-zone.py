#!/usr/bin/env python3
import requests
import dns.rdataset
import dns.zonefile
import dns.zone
import dns.resolver
import dns.query
import re
import sys
import argparse
import json
from typing import cast, Union, Any

def readSecret(secretPath):
    with open(secretPath) as f:
            mySecret = f.readline()
            return mySecret

def rdtypeToF5DX(rdtype):
    rdtype = cast(dns.rdatatype, rdtype)
    if rdtype == dns.rdatatype.A:
        return "a_record"
    elif rdtype == dns.rdatatype.AAAA:
        return "aaaa_record"
    elif rdtype ==  dns.rdatatype.CAA:
        return "caa_record"
    elif rdtype == dns.rdatatype.CNAME:
        return "cname_record"
    elif rdtype == dns.rdatatype.MX:
        return "mx_record"
    elif rdtype == dns.rdatatype.NS:
        return "ns_record"
    elif rdtype == dns.rdatatype.PTR:
        return "ptr_record"
    elif rdtype == dns.rdatatype.SRV:
        return "srv_record"
    elif rdtype == dns.rdatatype.TXT:
        return "txt_record"
    elif rdtype == dns.rdatatype.SOA:
        return "soa_record"
    else:
        raise Exception("Undefined. No F5 conversion type")

def endify(itr):
        """
        Like enumerate() except returns a bool if this is the last item instead of the number
        """
        itr = iter(itr)
        has_item = False
        ended = False
        next_item = None
        while not ended:
            try:
                next_item = next(itr)
            except StopIteration:
                ended = True
            if has_item:
                yield ended, item
            has_item = True
            item = next_item

def main():
    parser = argparse.ArgumentParser(description="Argument Parser") 
    parser.add_argument("domain", type=str, help="Domain to Transfer")
    parser.add_argument("dns_server", type=str, help="Server to query for transfer")
    
    args = parser.parse_args()

    pubIP = requests.get("https://api.ipify.org", verify=False).content.decode("utf8")
    print("Please ensure zone transfers are allowed from: {}".format(pubIP))

    #soa_answer = dns.resolver.resolve(args.domain, "SOA")
    #master_answer = dns.resolver.resolve(soa_answer[0].mname, "A")

    zone = dns.zone.from_xfr(dns.query.xfr(args.dns_server, args.domain))
    #print(z.nodes.keys())
    #print("\"defautl_rr_set_group\": [")
    _defaultRrSet = "\t\t\t\"default_rr_set_group\": [\n"
    needsDelimeter = False
    for lName, name in endify(sorted(zone.nodes.keys())):
        if name.to_text() == "@":
            recordName = ""
        else:
            recordName = name.to_text()
        node = cast(dns.node.Node, zone.get_node(name))
        for lR, r in endify(node.rdatasets):
            rdata = ''
            #F5 min ttl 60
            if r.ttl < 60:
                r.ttl = 60
            if r.rdtype == dns.rdatatype.SOA:
                needsDelimeter = False
                continue
            if r.rdtype == dns.rdatatype.NS:
                needsDelimeter = False
                continue
            if needsDelimeter:
                _defaultRrSet += ",\n"
                needsDelimeter = False
            if r.rdtype == dns.rdatatype.CNAME:
                valueArray = False
            else:
                valueArray = True
            #print(r.rdtype)
            #print("{}\t{}".format(r.ttl, r.to_text()))
            #print("{")
            #print("\t\"ttl\"\": {},".format(r.ttl))
            #print("\t\"{}\": ".format(rdtypeToF5DX(r.rdtype)) + "{")
            #print("\t\t\"name\": \"{}\",".format(name))
            for end, d in endify(r):
                #somehow check for last record to determine comma
                if r.rdtype == dns.rdatatype.TXT:
                    rdata += "{}".format(d.to_text())
                elif r.rdtype == dns.rdatatype.MX:
                    mxRecord = re.sub('\.$', '', d.to_text().split(" ")[1])
                    priority = d.to_text().split(" ")[0]
                    rdata += "{{\n\t\t\t\t\t\t\t\t\"domain\": \"{}\",\n\t\t\t\t\t\t\t\t\"priority\": {}\n\t\t\t\t\t\t\t}}".format(mxRecord, priority)
                else:
                    rdata += "\"{}\"".format(d.to_text())
                if not end:
                    rdata += ",\n\t\t\t\t\t\t\t"
            #rdata = rdata + "\t\t]"
            #print("\t}")
            if valueArray:
                _defaultRrSet += "\t\t\t\t{{\n\t\t\t\t\t\"ttl\": {},\n\t\t\t\t\t\"{}\": {{\n\t\t\t\t\t\t\"name\": \"{}\",\n\t\t\t\t\t\t\"values\": [\n\t\t\t\t\t\t\t{}\n\t\t\t\t\t\t]\n\t\t\t\t\t}}\n\t\t\t\t}}".format(r.ttl, rdtypeToF5DX(r.rdtype), recordName, rdata)
            else:
                _defaultRrSet += "\t\t\t\t{{\n\t\t\t\t\t\"ttl\": {},\n\t\t\t\t\t\"{}\": {{\n\t\t\t\t\t\t\"name\": \"{}\",\n\t\t\t\t\t\t\"value\": {}\n\t\t\t\t\t}}\n\t\t\t\t}}".format(r.ttl, rdtypeToF5DX(r.rdtype), recordName, rdata)
            if not lR:
                needsDelimeter = True
            else:
                needsDelimeter = False
        if not lName:
            _defaultRrSet += ",\n"
    _defaultRrSet += "\n\t\t\t]"

    f5xcZone = "{{\n\t\"metadata\": {{\n\t\t\"name\": \"{}\",\n\t\t\"namespace\": \"system\",\n\t\t\"labels\": {{}},\n\t\t\"annotations\": {{}},\n\t\t\"disable\": false\n\t}},\n\t\"spec\": {{\n\t\t\"primary\": {{\n\t\t\t\"default_soa_parameters\": {{}},\n\t\t\t\"dnssec_mode\": {{\n\t\t\t\t\"disable\": {{}}\n\t\t\t}},\n\t\t\t\"rr_set_group\": [],\n{}\n\t\t}}\n\t}}\n}}".format(args.domain, _defaultRrSet)

    print(f5xcZone)

    #for arecord in z.iterate_rdatas(dns.rdatatype.A):
    #    print("{}\t{}\t{}".format(arecord[0], arecord[1], arecord[2]))

############################ GLOBALS ###############################

api_url = "https://" + readSecret(".secrets/.consoleDomain") + ".ves.volterra.io/api/config/dns/namespaces/system/dns_zones"

api_headers = {
            "Authorization" :   readSecret(".secrets/.apiToken"),
                "Accept"        :   "application/json"
                }

if __name__ == "__main__":
    main()

