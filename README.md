# hmicrawler
## SIMATIC HMI Miniweb Crawler

2023.05.12
this script gets all json files from a siemens hmi  
the json files stored on the SDCARD see storage configuration  
the filename is defined as follow [ProductionNR]_[MachineName]_[YYMMDDHHmmSS].json  
the Warnings and Errorlogs are stored in [AlarmeWarnungen]_[MachineName]_[Nr].csv  
the Configfiles are downloadable by using the backup argument  
example:  
```
    python3 hmicrawler.py --url 'https://192.168.10.200:443' --dest '/tmp/fish' --backup --user '#youruser#' --password '#mypwd#'
```