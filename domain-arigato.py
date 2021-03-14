import requests
import urllib3
from termcolor import colored
from urllib.parse import urlparse
import sys
import json

#prevent urllib from comaplaining about no cert verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

filepath = sys.argv[1]
resultsfile = sys.argv[2]

def colorize_status_code(status_code):
    if status_code in [500,502,503]:
        return colored(status_code,'red')
    else:
        return colored(status_code,'green')

def is_same_domain(host_a,host_b):
    ra = host_a[::-1]
    rb = host_b[::-1]
    return ra.startswith(rb) or rb.startswith(ra)

def is_redirect(start_url, redirect_urls):
    if len(redirect_urls) == 0:
        return (False,None)
    
    start_host=urlparse(start_url).hostname
    for u in redirect_urls:
        target_host=urlparse(u).hostname
        if target_host and not is_same_domain(start_host,target_host):
            return (True, target_host)
    return (False,None)

def check_url(url):
    res = {"url":url}
    try:
        r = requests.get(url, timeout=5, verify=False )
        redirs = [x.headers['location'] for x in r.history]
        res["status"]=r.status_code
        res["redirects"]=redirs
        res["is_redirect"],res["target_host"] = is_redirect(url,redirs)
        if res["is_redirect"]:
            print("\t[*] {0} 🠒 {1}".format(url,res["target_host"]))
        else:
            print("\t[*] {0} {1}".format(url,colorize_status_code(r.status_code)))

    except (TypeError,IndexError) as te:
        raise te
    except Exception as ex:
       print("\t[*] {0} error {1}".format(url,colored(type(ex).__name__,'red')))
       res["error"]=type(ex).__name__
    return res
 

def update_statistics(domain_data):
    domain_data["stats"]={}
    domain_data["stats"]["global"]={"errors":0,"redirects":0,"total":0}
    for p in domain_data["protocols"]:
        stats={"errors":0,"redirects":0,"total":0}
        for r in domain_data["protocols"][p]["requests"]:
            stats["total"]+=1
            domain_data["stats"]["global"]["total"]+=1
            if 'error' in r:
                stats["errors"] +=1
                domain_data["stats"]["global"]["errors"]+=1
            if 'is_redirect' in r and r['is_redirect']:
                stats["redirects"] +=1
                domain_data["stats"]["global"]["redirects"]+=1
        
        domain_data["stats"][p]=stats
    return domain_data

def check_domain_http(domain):
    print("[*] {0}".format(domain))
    d_meta = {"domain":domain}
    d_meta["protocols"]= {}
    d_meta["protocols"]["http"]={"requests":[check_url("http://{0}/".format(domain)), check_url("http://www.{0}/".format(domain))]}
    d_meta["protocols"]["https"]={"requests":[check_url("https://{0}/".format(domain)), check_url("https://www.{0}/".format(domain))]}

    d_meta = update_statistics(d_meta)
    return d_meta


with open(filepath) as fp:
    res=[]
    for cnt, line in enumerate(fp):
        domain = line.strip()
        res+=[check_domain_http(domain)]

with open(resultsfile,'w+') as fpres:
    fpres.write(json.dumps(res))