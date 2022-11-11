#!/usr/bin/env python3
import requests
import dns.rdataset
import dns.zonefile
import dns.zone
import os, glob
import json
import re
from tools.helpers import *
from tools.f5 import *


def main():
    api_url = "https://{}.console.ves.volterra.io/api/config/dns/namespaces/system/dns_zones".format(readSecret(".secrets/.consoleDomain"))

    api_headers = {
        "Authorization" :   "{}".format(readSecret(".secrets/.apiToken")),
        "Accept"        :   "application/json"
    }

    path = 'zones/'
    for filename in glob.glob(os.path.join(path, '*.zf')):
        with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
            dnsZone = dns.zone.from_file(f)
            defaultRR = ZoneNodesToF5Json(dnsZone)
            zoneName = re.sub('\.zf', '', os.path.basename(filename))
            print("Processing Zone {}".format(zoneName))

            jBody = {
                "metadata": {
                    "name": zoneName,
                    "namespace": "system",
                    "labels": {},
                    "annotations": {},
                    "disable": False
                },
                "spec": {
                    "primary": {
                        "default_soa_parameters": {},
                        "dnssec_mode": {
                            "disable": {}
                        },
                        "rr_set_group": [],
                        "default_rr_set_group": defaultRR
                    }
                }
            }
        #print(json.dumps(jBody, indent=4))
        print("Attempting to create zone {} at:\n{}".format(zoneName, api_url))
        createZone = requests.post(api_url, verify=False, headers=api_headers, json=jBody)

        print(createZone.json())

if __name__ == "__main__":
    main()