# hmicrawler
## SIMATIC HMI Miniweb Crawler

2023.05.12 - by andreas.kraxner@hblfa-tirol.at
this script gets all json files from a siemens hmi
the json files stored on the SDCARD see storage configuration
example:
```
    python3 hmicrawler.py --url 'https://192.168.10.200:443' --dest '/tmp/fish' --backup --user '#youruser#' --password '#mypwd#'
```