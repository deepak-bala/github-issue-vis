import base64
import string
import sys

__author__ = 'Deepak Bala'

import httplib as http
import json
from optparse import OptionParser

from datetime import datetime


ep = datetime.utcfromtimestamp(0)

def main():
    parser = OptionParser()
    parser.add_option("-r", "--repo", help="The repo name in github")
    parser.add_option("-u", "--user", help="The user name in github")
    parser.add_option("-p", "--passw", help="Your github password (Required for private repos)")
    (options, args) = parser.parse_args()
    headers = {}
    if options.passw is not None:
        print("Adding basic auth header")
        auth = 'Basic ' + string.strip(base64.encodestring(options.user + ':' + options.passw))
        headers = {"Authorization": auth}

    connection = http.HTTPSConnection(host='api.github.com')
    url = "/repos/" + options.user + "/" + options.repo + "/issues?state=closed"
    print("Triggering " + str(url))
    resp = get_issues(connection,url, headers)
    issues = resp[0]
    links = resp[1]
    counter = 0
    while links is not None and 'next' in links.split(',')[0]:
        next_raw = links.split(';')[0]
        next_raw_len = len(next_raw)
        next = next_raw[1:next_raw_len-1]
        print('Found next ' + next)
        temp = get_issues(connection,next,headers)
        issues.extend(temp[0])
        links = temp[1]
        counter += 1
        # Note - un-comment to analyze fewer issues
        # if counter > 5:
        #     break

    print("Found " + str(len(issues)) + " issues")

    created_list = []
    closed_list = []
    for issue in issues:
        created = format_date(issue['created_at'])
        closed = format_date(issue['closed_at'])
        created_list.append(get_seconds(created))
        closed_list.append(get_seconds(closed))
    created_list = sorted(created_list)
    closed_list = sorted(closed_list)
    print('--------- Issue timeline ---------')
    for counter in range(len(created_list)):
        print(str(counter) + "," + str(created_list[counter]) + "," + str(closed_list[counter]))

    print_issue_timeline(created_list,closed_list)


def get_issues(connection, url, reqHeaders):
    connection.request("GET", url , headers=reqHeaders)
    issue_response = connection.getresponse()
    status = issue_response.status
    if status != 200:
        print('Something bad happened - ' + str(issue_response.reason))
        sys.exit()
    data = issue_response.read()
    issue_struct = json.loads(data)
    links = issue_response.getheader('Link')
    return [issue_struct,links]

def format_date(date):
    dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    return dt

def get_seconds(date):
    secs = (date - ep).total_seconds()
    return secs

def print_issue_timeline(created_list,closed_list):
    print('--------- Open / Closed issues at any time ---------')
    closedCounter = 0
    crete_len = len(created_list)
    createdCounter=0
    created = created_list[createdCounter]
    closed = closed_list[closedCounter]
    flag = False
    while True:
        while created <= closed:
            createdCounter += 1
            print(str(created) + "," + str(createdCounter) + "," + str(closedCounter) )
            if createdCounter >= crete_len:
                break
            created = created_list[createdCounter]
        while closed <= created:
            closedCounter += 1
            print(str(closed) + "," + str(createdCounter) + "," + str(closedCounter) )
            if closedCounter >= crete_len:
                break
            closed = closed_list[closedCounter]
        if createdCounter >= crete_len:
            for counter in range(closedCounter , crete_len):
                closedCounter += 1
                closed = closed_list[counter]
                print(str(closed) + "," + str(createdCounter) + "," + str(closedCounter) )
            break

main()