import math
import lxml.html
from bs4 import BeautifulSoup
import requests
import json
import sys
import argparse
import datetime
from progress.bar import Bar
import pycountry 

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# your binaryedge.io API key
BE_API_KEY = 'API KEY'

powered = bcolors.GREEN + """
dw-leak-scan - scan open databases - powered by https://www.binaryedge.io/
https://github.com/zhzhussupovkz/dw-leak-scan
""" + bcolors.ENDC
print (powered)

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

group = parser.add_argument_group("Pages")

parser.add_argument("--elastic", help = "elasticsearch", action = 'store_true')
parser.add_argument('--kibana', help = 'kibana', action = 'store_true')
parser.add_argument("--mongodb", help = "mongodb", action = 'store_true')
parser.add_argument("--couchdb", help = "couchdb", action = 'store_true')
parser.add_argument("--cassandra", help = "cassandra", action = 'store_true')
parser.add_argument("--listing", help = "listing directory", action = 'store_true')
parser.add_argument("--filter", help = "filter for BinaryEdge", default = "")
parser.add_argument("--size", help = "size filter for indices", default = 1024*1024*1000, type = int)

group.add_argument('--first', help = 'first page', default = 1, type = int)
group.add_argument('--last', help = 'last page', default = 1, type = int)

args = parser.parse_args()

elastic = args.elastic
kibana = args.kibana
mongodb = args.mongodb
couchdb = args.couchdb
cassandra = args.cassandra
listing = args.listing
query = args.filter
first = args.first
last = args.last
size = args.size

if last == first:
    last = first + 1
elif last < first:
    last = first + 1

elastic_q = "type:%22elasticsearch%22"
kibana_q = "product:%22kibana%22"
mongodb_q = "type:%22mongodb%22"
couchdb_q = "product:%22couchdb%22"
listing_q = '%22Index of /%22'
cassandra_q = "type:%22cassandra%22"

class minSize:
    MONGODB = 23 * 1024 * 1024 * 1024

# format docs count
def millify(n):
    millnames = ['',' k',' mln',' bln',' trln']
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

# format index size human readable
def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

# get country name
def get_country(code):
    country = pycountry.countries.get(alpha_2=code.upper())
    country_name = country.name if country else str(code.upper())
    return " " + str(country_name)

# get date
def get_date(ts):
    d = datetime.datetime.fromtimestamp(int(ts/1e3))
    return ' {}'.format(d.strftime("%Y-%m-%d"))

def binary_edge_request(query, page):
    headers = {'X-Key': BE_API_KEY}
    url = 'https://api.binaryedge.io/v2/query/search?query=' + query + '&page=' + str(page)
    req = requests.get(url, headers=headers)
    req_json = json.loads(req.content)
    try:
        if req_json.get("status"):
            print (bcolors.YELLOW + req_json.get("status") + ' ' + req_json.get("message") + bcolors.ENDC)
        else:
            print (bcolors.GREEN + "total results: " + str(req_json.get('total')) + bcolors.ENDC)
    except:
        print (bcolors.RED + "error :(" + bcolors.ENDC)
        sys.exit()
    return req_json.get("events")

# normalize elasticsearch results
def normalize_elastic(results):
    if results:
        for service in results:
            print(bcolors.BLUE + 'http://' + service['target']['ip'] + ":" + str(service['target']['port']) + "/_cat/indices"
             + get_country(service['origin']['country'])
             + get_date(service['origin']['ts'])
             + bcolors.ENDC)
            print(bcolors.PURPLE + service['result']['data']['cluster_name'] + bcolors.ENDC)
            try:
                for i in service['result']['data']['indices']:
                    if i['size_in_bytes'] > size:
                        print(bcolors.YELLOW + i['index_name'] + ": " + millify(i['docs'])
                         + ", size: " + sizeof_fmt(i['size_in_bytes']) + bcolors.ENDC)
            except:
                print("no indices")
            print("-----------------------------")

# normalize kibana results
def normalize_kibana(results):
    if results:
        for service in results:
            print(bcolors.BLUE + 'http://' + service['target']['ip'] + ":" + str(service['target']['port']) + "/app/kibana#/discover?_g=()"
             + get_country(service['origin']['country'])
             + get_date(service['origin']['ts'])
             + bcolors.ENDC)
            print(bcolors.YELLOW + "server status: " + service['result']['data']['state']['state'] + bcolors.ENDC)
            print("-----------------------")

# normalize mongodb results
def normalize_mongodb(results):
    if results:
        for service in results:
            print(bcolors.BLUE + 'IP: ' + service['target']['ip'] + ":" + str(service['target']['port'])
             + get_country(service['origin']['country'])
             + get_date(service['origin']['ts'])
             + bcolors.ENDC)
            if not service['result']['error']:
                try:
                    if service['result']['data']['listDatabases']['totalSize'] > minSize.MONGODB:
                        print(bcolors.YELLOW + "size: " + sizeof_fmt(
                            service['result']['data']['listDatabases']['totalSize']) + bcolors.ENDC)

                        for database in service['result']['data']['listDatabases']['databases']:
                            if database['empty'] != 'true':
                                print(bcolors.YELLOW + "db: " + database['name'] + 
                                ", size: " + sizeof_fmt(database['sizeOnDisk']) + bcolors.ENDC)
                                print('collections:')
                                for collection in database['collections']:
                                    print(bcolors.GREEN + collection['name'] + bcolors.ENDC)
                        print("-----------------------------")
                    else:
                        print(bcolors.RED + "total size is only " + 
                        sizeof_fmt(service['result']['data']['listDatabases']['totalSize']) + 
                        " which is below default - " + sizeof_fmt(217000000) + bcolors.ENDC)
                        print("-----------------------------")
                except:
                    pass
            else:
                print("-----------------------------")

# normalize couchdb
def normalize_couchdb(results):
    if results:
        for service in results:
            print(bcolors.BLUE + 'http://' + service['target']['ip'] + ":" + str(service['target']['port']) +"/_all_dbs"
             + get_country(service['origin']['country'])
             + get_date(service['origin']['ts'])
             + bcolors.ENDC)
            try:
                couch_json = json.loads(service['result']['data']['response']['body'])
                print(bcolors.YELLOW + "status code: " + str(service['result']['data']['response']['statusCode']) + bcolors.ENDC)
                print(bcolors.PURPLE + "vendor: " + couch_json['vendor']['name'] + bcolors.ENDC)
                print('features:')
                for i in couch_json['features']:
                    print(bcolors.GREEN + i + bcolors.ENDC)
            except Exception as e:
                if 'state' in service['result']['data']:
                    print(bcolors.YELLOW + "server status: " + service['result']['data']['state']['state'] + bcolors.ENDC)
                else:
                    print(bcolors.RED + "cannot retrieve information" + bcolors.ENDC)

            print("-----------------------------")

# normalize cassandra
def normalize_cassandra(results):
    if results:
        for service in results:
            print(bcolors.BLUE + 'IP: ' + service['target']['ip'] + ":" + str(service['target']['port'])
             + get_country(service['origin']['country'])
             + get_date(service['origin']['ts'])
             + bcolors.ENDC)
            try:
                print(bcolors.PURPLE + "cluster name: " + service['result']['data']['info'][0]['cluster_name'] + bcolors.ENDC)
                print(bcolors.YELLOW + "datacenter: " + service['result']['data']['info'][0]['data_center'] + bcolors.ENDC)

                for keyspace in service['result']['data']['keyspaces']:
                    if keyspace == 'system' or keyspace =="system_traces" or keyspace == "system_schema" or keyspace=='system_auth' or keyspace=='system_distributed':
                        pass
                    else:
                        print(bcolors.GREEN + "keyspace: " + keyspace + bcolors.ENDC)
                        print("tables: ")
                        for table in service['result']['data']['keyspaces'][keyspace]['tables']:
                            print(bcolors.YELLOW + table + bcolors.ENDC)
                print("-----------------------------")
            except Exception as e:
                print("-----------------------------")
                pass

# normalize listing
def normalize_listing(results):
    if results:
        for service in results:
            dir = False
            schema = "https" if service['target']['port'] == 443 else "http"
            print(bcolors.BLUE + schema + '://' + service['target']['ip'] + ":" + str(service['target']['port'])
             + get_country(service['origin']['country'])
             + get_date(service['origin']['ts'])
             + bcolors.ENDC)
            
            #print (service)

            try:
                print(bcolors.PURPLE + "product: " + 
                service['result']['data']['service']['product'] + bcolors.ENDC)

                if 'hostname' in service['result']['data']['service']:
                    print(bcolors.YELLOW + "hostname: " + 
                    service['result']['data']['service']['hostname'] + bcolors.ENDC)
                html_code = service['result']['data']['service']['banner']
            except KeyError:
                if 'response' in service['result']['data']:
                    print(bcolors.YELLOW + "status code: " + str(service['result']['data']['response']['status']['code']) + bcolors.ENDC)
                    html_code = service['result']['data']['response']['body']['content']
                else:
                    html_code = ""

            soup = BeautifulSoup(html_code, features="html.parser")
            for project in soup.find_all("a", href=True):
                try:
                    if project.contents[0] == "Name" or project.contents[0] == "Last modified" or project.contents[0] == "Size" or project.contents[0] == "Description" or project.contents[0] == "../":
                        dir = True
                        pass

                    if dir == True:
                        if project.contents[0] == "Name" or project.contents[0] == "Last modified" or project.contents[
                            0] == "Size" or project.contents[0] == "Description" or project.contents[0] == "../":
                                pass
                        else:
                            print(bcolors.GREEN + str(project.contents[0]) + bcolors.ENDC)
                except:
                    pass
            print("-----------------------------")



if elastic:
    for page in range(first, last):
        print('----------------------------------elasicsearch result - page ' + 
        str(page) + 
        '--------------------------------')
        es_results = binary_edge_request(elastic_q + " " + query, page)
        normalize_elastic(es_results)

if kibana:
    for page in range(first, last):
        print('----------------------------------kibana result - page ' + 
        str(page) + 
        '--------------------------------')
        kibana_results = binary_edge_request(kibana_q + " " + query, page)
        normalize_kibana(kibana_results)

if mongodb:
    for page in range(first, last):
        print('----------------------------------mongodb result - page ' + 
        str(page) + 
        '--------------------------------')
        mongodb_results = binary_edge_request(mongodb_q + " " + query, page)
        normalize_mongodb(mongodb_results)

if couchdb:
    for page in range(first, last):
        print('----------------------------------couchdb result - page ' + 
        str(page) + 
        '--------------------------------')
        couchdb_results = binary_edge_request(couchdb_q + " " + query, page)
        normalize_couchdb(couchdb_results)

if cassandra:
    for page in range(first, last):
        print('----------------------------------cassandra result - page ' + 
        str(page) + 
        '--------------------------------')
        cassandra_results = binary_edge_request(cassandra_q + " " + query, page)
        normalize_cassandra(cassandra_results)

if listing:
    for page in range(first, last):
        print('----------------------------------listing result - page ' + 
        str(page) + 
        '--------------------------------')
        listing_results = binary_edge_request(listing_q + " " + query, page)
        normalize_listing(listing_results)
