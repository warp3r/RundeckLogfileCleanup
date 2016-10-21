#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import xml.etree.ElementTree as ET
import time
import json
import sys


# Returns list of all the project names
def get_projects():
    global PROPERTIES
    global HEADERS
    project_names = []
    r=""
    try:
        url = URL + 'projects'
        r = requests.get(url, headers=HEADERS, verify=False,timeout=PROPERTIES['TIMEOUT'])
        root = ET.fromstring(r.text.encode('utf-8'))
        for project in root:
            for name in project.findall('name'):
                project_names.append(name.text)
    except:
        print "Problem with project listing {0}".format(r)
        pass
    return project_names

# Gets executions for projects
def getExecutions(project):
    global PROPERTIES
    global HEADERS
    executions = []

    try:
        url = URL + 'project/' + project + '/executions?olderFilter=' + str(PROPERTIES['MAXIMUM_DAYS']) + 'd&max=' + str(PROPERTIES['PAGE_SIZE'])
        r = requests.get(url, headers=HEADERS, verify=False,timeout=PROPERTIES['TIMEOUT'])
        root = ET.fromstring(r.text.encode('utf-8'))
        print root.attrib
        for execution in root:
            executions.append(execution.attrib['id'])
    except:
        print "Problem with execution listing listing {0}".format(r)
        pass

    return executions

#API call to delete an execution by ID
def delete_execution(execution_id):
    global PROPERTIES
    global HEADERS
    url = URL + 'execution/'+execution_id
    try:
        r = requests.delete(url, headers=HEADERS, verify=False,timeout=PROPERTIES['TIMEOUT'])
        if PROPERTIES['VERBOSE']:
            print "            Deleted execution id {0} {1} {2}".format( execution_id, r.text, r )
    except:
        print "could not delete"
        pass

# API call to delete multiple executions
def delete_executions(id_list):
    global PROPERTIES
    global HEADERS
    url = URL + 'executions/delete'
    jsonvar = "[" + ",".join(id_list) + "]"
    try:
        r = requests.post(url, headers=HEADERS, data=jsonvar, verify=False,timeout=PROPERTIES['TIMEOUT'])
        if PROPERTIES['VERBOSE']:
            print "            Deleted executions id {0} {1} {2}".format( jsonvar, r.text, r )
    except:
        raise


#
# Main
#
setting_filename = sys.argv[1] if len(sys.argv)>1 else 'properties.json'
with open(setting_filename,'r') as props_file:
    PROPERTIES = json.load( props_file )

protocol='http'
if PROPERTIES['SSL']:
    protocol='https'
    # disable warnings about unverified https connections
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

URL = '{0}://{1}:{2}/api/{3}/'.format(protocol,PROPERTIES['RUNDECKSERVER'],PROPERTIES['PORT'],PROPERTIES['API_VERSION'])
HEADERS = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': PROPERTIES['API_KEY'] }

TODAY = int(round(time.time() * 1000))

for project in get_projects():
    print project
    executions = getExecutions(project)
    while len(executions) > 0:
        #for execution in executions:
        #    delete_execution(execution)
        delete_executions(executions)
        executions = getExecutions(project)

