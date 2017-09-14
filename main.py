#!/usr/bin/python
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from domoticz import Domoticz
import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    nowUTC = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    domoticzurl = "http://141.69.58.244:8080"
    timeLimitStart = datetime.timedelta(hours=2)
    heatingActive = False
    heatingTemp = 26.0
    coolTemp = 15.0
    currentTemp = float(Domoticz(domoticzurl).get_thermostat_value(19))
    now=datetime.datetime.now()


    print("#=~="*20)
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            print('\n')
            print(calendar_list_entry['summary'])
            eventsResult=service.events().list(calendarId=calendar_list_entry['id'], timeMin=nowUTC, maxResults=10, singleEvents=True, orderBy='startTime').execute()
            events=eventsResult.get('items', [])
            if not events:
                print('No upcoming events found.')
            for event in events:
                try:
                    start = datetime.datetime.strptime(event['start']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S')
                    end = datetime.datetime.strptime(event['end']['dateTime'][:19], '%Y-%m-%dT%H:%M:%S')
                    print(start - now, event['summary'].encode('utf-8'))
                    if event['location'] == 'k003' and (start - timeLimitStart < now) and (now < end):
                        heatingActive = True
                        if currentTemp == heatingTemp:
                            print('***   Heating already active   ***')
                        if currentTemp == coolTemp:
                            print("***   Activating heating   ***")
                            Domoticz(domoticzurl).set_thermostat_value(19, heatingTemp)
                        break
                except KeyError:
                    pass
            if heatingActive:
                break
        if heatingActive:
            break
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    if not heatingActive and currentTemp == heatingTemp:
        print('***   No events in sight. Setting heating to coolTemp   ***')
        Domoticz(domoticzurl).set_thermostat_value(19, coolTemp)
    if currentTemp not in [coolTemp, heatingTemp]:
        print('***   Manual override detected   ***')

    '''Reset temerature during night if override has not been revoked'''
    start = datetime.time(23, 40, 0)
    end = datetime.time(23, 50, 0)
    now = now.time()
    if start < now and now < end:
        print("***   Override detected and not reset. Setting back to cool temp.   ***")
        Domoticz(domoticzurl).set_thermostat_value(19, coolTemp)

if __name__ == '__main__':
    main()

