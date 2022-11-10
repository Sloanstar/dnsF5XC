#!/usr/bin/env python3
import requests
import dns.rdataset
import dns.zonefile
import dns.zone

def readSecret(secretPath):
    with open(secretPath) as f:
        mySecret = f.readline().strip()
        return mySecret

api_url = "https://{}.console.ves.volterra.io/api/config/dns/namespaces/system/dns_zones".format(readSecret(".secrets/.consoleDomain"))

api_headers = {
    "Authorization" :   "{}".format(readSecret(".secrets/.apiToken")),
    "Accept"        :   "application/json"
}

zonesResp = requests.get(api_url, headers=api_headers, verify=False)
#print (response.json())

zonesJson = zonesResp.json()
for zonesItem in zonesJson['items']:
    #print("Zone Ftch: " + api_url + "/" + zonesItem['name'])
    zoneResp = requests.get(api_url + "/" + zonesItem['name'], headers=api_headers, verify=False)
    zoneJson = zoneResp.json()
    #print(zoneJson['metadata'])
    #print(zoneJson['spec']['secondary']['zone_file'])
    f = open("", "rt")
    #dnsZone = dns.zonefile.read_rrsets(zoneJson['spec']['secondary']['zone_file'], origin=zonesItem['name'], relativize=True, rdclass=None)
    dnsZone = dns.zone.from_file(f)
    print(dnsZone.to_text())
    #for zoneItem in zoneJson['items']:
        #print(zoneItem)
