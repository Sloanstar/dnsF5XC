#!/usr/bin/env python3
import requests
import argparse
from typing import cast, Union, Any

def readSecret(secretPath):
    with open(secretPath) as f:
            mySecret = f.readline().strip()
            return mySecret

def main():
    parser = argparse.ArgumentParser(description="Argument Parser") 
    parser.add_argument("domain", type=str, help="Domain to Transfer")
    args = parser.parse_args()

    api_url = "https://{}.console.ves.volterra.io/api/config/dns/namespaces/system/dns_zones/{}".format(readSecret(".secrets/.consoleDomain"), args.domain)

    api_headers = {
        "Authorization" :   readSecret(".secrets/.apiToken"),
        "Accept"        :   "application/json"
    }

    body = "{{\n\t\"fail_if_referred\": true,\n\t\"name\": {}\n\t\"namespace\": \"system\"\n}}".format(args.domain)
    print(body)
    deleteZone = requests.delete(api_url, verify=False, headers=api_headers).content.decode("utf8")
    print(deleteZone)

############################ GLOBALS ###############################

if __name__ == "__main__":
    main()

