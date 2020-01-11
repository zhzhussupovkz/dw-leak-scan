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
python scan.py --elastic --first 3 --last 4 --filter "book"
```

## scanner has been made for educational purposes only.