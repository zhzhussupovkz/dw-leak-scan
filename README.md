# dw-leak-scan
Scan open databases - powered by [https://www.binaryedge.io/](https://www.binaryedge.io/)

**PUT API KEY**:
```python
#...

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
BE_API_KEY = 'your binaryedge.io API key'

#...
```

## Queries:
Read binaryedge's API V2 Documentation:
[https://docs.binaryedge.io/api-v2/](https://docs.binaryedge.io/api-v2/)

## Examples
Search open elasticsearch databases from RU (1-3 pages):
```console
python scan.py --elastic --first 1 --last 3 --filter "country:RU"
```

Search open mongodb databases with keyword "book" (3-4 pages):
```console
python scan.py --mongodb --first 3 --last 4 --filter "book"
```

Search open listing with keyword "facebook.csv" (1 page):
```console
python scan.py --listing --first 1 --filter "facebook.csv"
```

Search open couchdb databases with keyword "linux" (5-9 pages):
```console
python scan.py --couchdb --first 5 --last 9 --filter "linux"
```
Search open cassandra databases with keyword "cookbook" (1-4 pages):
```console
python scan.py --cassandra --first 1 --last 4 --filter "cookbook"
```

## scanner has been made for educational purposes only.