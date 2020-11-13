from __future__ import print_function
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import datetime
import re
import html2text

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def tokenAuth():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    path = os.getcwd() + '/dev/repositories/CodeMailAuto/'
    if os.path.exists(path + 'token.pickle'):
        with open(path + 'token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # path = 'credentials.json'
            flow = InstalledAppFlow.from_client_secrets_file(
                path + 'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(path + 'token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def decode(encodedStr):
    decodedBytes = base64.urlsafe_b64decode(encodedStr)
    return str(decodedBytes, 'utf-8')


def checkUnread():
    # Get UNREAD messages from 'daily@techseries.dev'
    results = SERVICE.users().messages().list(
        userId='me', q='from:{}'.format(CODE_DAILY_MAIL), labelIds='UNREAD').execute()
    messageComplexIds = results.get('messages', [])
    ids = []
    headers = []

    for messageComplexId in messageComplexIds:
        ids.append(messageComplexId['id'])

    if len(ids) > 0:
        for id in ids:
            results = SERVICE.users().messages().get(userId='me', id=id).execute()
            headers = results.get('payload', [])['headers']

    else:
        print('No daily today :/')

    subject = ''
    for header in headers:
        if header['name'] == 'Subject':
            subject = header['value']

    createPythonFile(subject, results)
    markAsRead(ids)


def createPythonFile(name, message):
    currentDate = datetime.datetime.now()
    name = name.replace('[Daily Problem] ', '{}'.format(str(
        currentDate.day) + '-' + str(currentDate.month) + '-' + str(currentDate.year) + ' '))

    path = os.getcwd() + '/dev/repositories/GoodMorningVietnam/{}.py'.format(name)
    dailyFile = open(path, 'a+')
    setFileText(message, dailyFile)
    dailyFile.close()
    runCode()


def setFileText(message, dailyFile):
    body = decode(message.get('payload')['body']['data'])
    startTrim = body.find('Hi')
    endTrim = body.find('Upgrade to PRO')
    body = body[startTrim:endTrim]
    dailyFile.write(html2text.html2text(body))


def runCode():
    path = os.getcwd() + '/dev/repositories/GoodMorningVietnam/'
    os.system('code {}'.format(path))


def markAsRead(ids):
    body = {
        'addLabelIds': [],
        'removeLabelIds': ['UNREAD']
    }
    if (len(ids) > 0):
        results = SERVICE.users().messages().modify(
            userId='me', id=ids[0], body=body).execute()


# Get or update authentification token and credentials
creds = tokenAuth()
SERVICE = build('gmail', 'v1', credentials=creds)
CODE_DAILY_MAIL = 'daily@techseries.dev'

checkUnread()
