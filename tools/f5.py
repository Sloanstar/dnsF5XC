#!/usr/bin/env python3
import dns.rdatatype
import dns.rdataset
from typing import cast, Union, Any
import re

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

def ZoneNodesToF5Json(zone):
    recordset=[]
    for name in sorted(zone.nodes.keys()):
        if name.to_text() == "@":
            recordName = ""
        else:
            recordName = name.to_text()
        node = cast(dns.node.Node, zone.get_node(name))
        records = {}
        for r in node.rdatasets:
            #F5 min ttl 60
            if r.ttl < 60:
                r.ttl = 60
            if r.rdtype == dns.rdatatype.SOA:
                continue
            if r.rdtype == dns.rdatatype.NS:
                continue
            if r.rdtype == dns.rdatatype.CNAME:
                record = {"name": recordName, "value": r[0].to_text()}
            else:
                record = {}
                rdata = []
                for d in r:
                    if r.rdtype == dns.rdatatype.SRV:
                        srv_rdata = {}
                        srv_split = d.to_text().split()
                        priority = int(srv_split[0])
                        weight = int(srv_split[1])
                        port = int(srv_split[2])
                        target = srv_split[3]
                        srv_rdata["priority"] = priority
                        srv_rdata["weight"] = weight
                        srv_rdata["port"] = port
                        srv_rdata["target"] = target
                        rdata.append(srv_rdata)
                    elif r.rdtype == dns.rdatatype.MX:
                        mx_rdata = {}
                        mx_split = d.to_text().split(" ")
                        priority = int(mx_split[0])
                        domain = re.sub('\.$', '', mx_split[1])
                        mx_rdata["priority"] = priority
                        mx_rdata["domain"] = domain
                        rdata.append(mx_rdata)
                    elif r.rdtype == dns.rdatatype.CAA:
                        caa_rdata = {}
                        caa_split = d.to_text().split()
                        flag = int(caa_split[0])
                        tag = caa_split[1]
                        value = re.sub('"', '', caa_split[2])
                        caa_rdata["flag"] = flag
                        caa_rdata["tag"] = tag
                        caa_rdata["value"] = value
                        rdata.append(caa_rdata)
                    elif r.rdtype == dns.rdatatype.TXT:
                        rdata.append(re.sub('"','',d.to_text()))
                    else:
                        rdata.append(d.to_text())
                record = {"name": recordName, "values": rdata}
            records = {"ttl": cast(int, r.ttl), rdtypeToF5DX(r.rdtype): record}
            recordset.append(records)

    return recordset