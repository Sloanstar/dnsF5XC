# dnsF5XC
Scripts to help onboard F5 Distributed Cloud DNS

## Purpose:
No way to onboard to F5XC for primary DNS without manually creating entries.

Requirements:
Tested with python3.8, dnsPython2.2.1, requests2.22.0

Secrets management:
Nothing fancy here, by default the scripts will look in a subdirectory .secrets for 2 files. The contents of these files are a single line as follows:
  .apiToken = the full API token generated from your F5XC instance with DNS rights.
    e.g. "APIToken sgr54fgs!zY347rgrew34wtw4trt"
  .consoleDomain = the domain/tenant id of your console instance.
    e.g. If your console url is foo.console.ves.volterra.io we're looking for "foo" here.

Script Purpose:

delete-zone.py            Delete specified zone from F5XC instance.
dump-zone.py              Dump zone from specified DNS server (AXFR) to STD out.
json-zone.py              Dump zone from specified DNS server (AXFR) to STD out in F5XC JSON format.
list-dns-zones.py         List all DNS zones defined in F5XC
migrate-zone-primary.py   Migrate zone from specified DNS server (AXFR) to F5XC as Primary Zone
parse-zonefile.py         Parse BIND zone files (*.zf) in the zones/ subdirectory and implement as Primary DNS Zone
