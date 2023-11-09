#!/usr/bin/env python3
# coding: utf8
"""
2023.05.12
this script gets all json files from a siemens hmi
the json files stored on the SDCARD see storage configuration
the filename is defined as follow [ProductionNR]_[MachineName]_[YYMMDDHHmmSS].json
the Warnings and Errorlogs are stored in [AlarmeWarnungen]_[MachineName]_[Nr].csv
the Configfiles are downloadable by using the backup argument
example:
    python3 hmicrawler.py --url 'https://192.168.10.200:443' --dest '/tmp/fish' --backup --user '#youruser#' --password '#mypwd#'
"""
import requests

#disable warning by change settings in the urllib3
requests.packages.urllib3.disable_warnings()
import re
import argparse
import os
import datetime
import json
from urllib.parse import quote

__author__ = "Andreas Kraxner"
__copyright__ = "Copyright 2023, tritondm"
__credits__ = [" Andreas Kraxner"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Andreas Kraxner"
__email__ = "andreas.kraxner@hblfa-tirol.at"
__status__ = "Production"

snitoken='%=Token'

cmd_getstorage='/StorageCardSD?UP=TRUE&FORCEBROWSE'
cmd_delstorage='?DELETE&UP=TRUE&SingleUseToken='
store_bef='/StorageCardSD/'
store_after='?UP=TRUE&FORCEBROWSE'

datum = datetime.datetime.now()

#get storage card
def get_data(url, dest, backup, presse, username, passwd):
    siteurl=url
    storage=dest
    session = requests.Session()
    session.post(siteurl + '/FormLogin', data={'Login': username, 'Password': passwd, 'Token': snitoken}, verify=False)
    if presse:
        regex_find_json = re.compile('\d{8}_\d{8}_[A-Z]{2}\d{1}_\d{12}.json')
    else:
        regex_find_json = re.compile('\d{8}_[A-Z]{2}\d{1}_\d{12}.json')

    regex_find_warnungcsv=re.compile('\w{15}_\w{2}\d{1}_\d{1}.csv')
    regex_find_backupfiles=re.compile('PTRCP_\w{13,23}_\d{1}.\w{3}')
    regex_find_token=re.compile(r'encodeURIComponent\(\"(.*?)\"\);')
    htmllist=session.get(siteurl + cmd_getstorage)
    if backup:
        if not os.path.exists(storage + 'backup'):
            os.mkdir(storage + 'backup')
        print("write backup")
    #print(htmllist.text)
    jsonlist=[]
    alarmcsv=[]
    backuplist=[]
    for line in htmllist:
        itemf = re.findall(regex_find_json, line.decode('utf-8', 'ignore'))
        itemfa = re.findall(regex_find_warnungcsv, line.decode('utf-8', 'ignore'))
        itemfbackup = re.findall(regex_find_backupfiles, line.decode('utf-8', 'ignore'))
        if re.findall(regex_find_token, line.decode('utf-8', 'ignore')):
            singleusetoken = re.findall(regex_find_token, line.decode('utf-8', 'ignore'))
        #create json list
        if len(itemf) > 0:
            if itemf[0] not in jsonlist:
                jsonlist.append(str(itemf[0]))
        if len(itemfa) > 0:
            if itemfa[0] not in alarmcsv:
                alarmcsv.append(str(itemfa[0]))
        if backup:
            if len(itemfbackup) > 0:
                if itemfbackup[0] not in backuplist:
                    backuplist.append(str(itemfbackup[0]))
    #get the jsonfiles
    for json in jsonlist:
        #print(json)
        jdata=session.get(siteurl + store_bef + json + store_after)
        with open(storage + json, 'wb') as f:
            f.write(jdata.content)
        f.close()
        print(storage + json)
        if checkjson(storage + json):
            try:
                print("json file  " + json + " is ok delete the file on remote site with token \n" + quote(singleusetoken[0]))
                session.get(siteurl + store_bef + json + cmd_delstorage + quote(singleusetoken[0]))
                #update get the token
                htmllistn = session.get(siteurl + cmd_getstorage)
                for linen in htmllistn:
                    if re.findall(regex_find_token, linen.decode('utf-8', 'ignore')):
                        singleusetoken = re.findall(regex_find_token, linen.decode('utf-8', 'ignore'))
            except:
                print("error cannot delete file on remote site\n")
        else:
            print("json file  " + json + " is NOK wait for close statement\n")

    for csv in alarmcsv:
        #print(json)
        csvdata=session.get(siteurl + store_bef + csv + store_after)
        with open(storage + csv, 'wb') as f:
            f.write(csvdata.content)
        f.close()
    if backup:
        for bkp in backuplist:
            #print(json)
            backupdata=session.get(siteurl + store_bef + bkp + store_after)
            with open(storage + 'backup/' + datum.strftime("%w") + bkp, 'wb') as f:
                f.write(backupdata.content)
            f.close()

def checkjson(filename):
    try:
        with open(filename, encoding='ISO-8859-1') as f:
            return json.load(f)
    except ValueError as e:
        print('invalid json: %s' % e)
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='url', required=True,
                    help="url example: http://192.168.1.200:6664")
    parser.add_argument('--dest', dest='dest', required=True,
                    help="destination path example: /tmp/kp1/")
    parser.add_argument('--user', dest='username', required=True,
                    help="Username of HMI")
    parser.add_argument('--password', dest='password', required=True,
                    help="Username of HMI")
    parser.add_argument('--backup',  action='store_true',
                    help="Saves all Receipes to filesystem - destination/backup/")
    parser.add_argument('--presse',  action='store_true',
                    help="only for Presse")
    args = parser.parse_args()
    get_data(str(args.url), str(args.dest), args.backup, args.presse, args.username, args.password)


if __name__ == "__main__":
    main()

