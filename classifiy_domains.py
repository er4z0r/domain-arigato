import json
import sys

#the JSON output produced by domain-arigato.py
datafile=sys.argv[1]


def is_redirector(domain_data):
    r = domain_data["stats"]["global"]["redirects"]
    e = domain_data["stats"]["global"]["errors"]
    t = domain_data["stats"]["global"]["total"]
    c = r / (t-e) if (t-e>0) else 0
    return (c>0.5, r, t)

def is_tumbleweed(domain_data):
    r = domain_data["stats"]["global"]["redirects"]
    e = domain_data["stats"]["global"]["errors"]
    t = domain_data["stats"]["global"]["total"]
    c = (e/t)
    
    return (c==1, e, t)


with open(datafile,'r') as fd:
    domain_data = json.load(fd)

for d in domain_data:
    d["classifications"]={}
    print("[*] {0}".format(d["domain"]))
    
    d["classifications"]["redirector"],r,t = is_redirector(d)
    print("\t[-] redirector: {0} ({1}/{2})".format(d["classifications"]["redirector"],r,t))
    
    d["classifications"]["tumbleweed"],e,t = is_tumbleweed(d)
    print("\t[-] tumbleweed: {0} ({1}/{2})".format(d["classifications"]["tumbleweed"],e,t))
