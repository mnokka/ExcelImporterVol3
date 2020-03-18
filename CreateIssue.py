# Create Issue to given JIRA
# Requires .netrc file for authentication
#
# 6.12.2016 mika.nokka1@gmail.com for Ambientia
# 
# NOTE: For POC removed .netrc authetication, using pure arguments
# NOTE: NOT TESTED with changes added using normal commandline usage!!!!
# (used via importing only)
# 

import datetime 
import time
import argparse
import sys
import netrc
import requests, os
from requests.auth import HTTPBasicAuth
# We don't want InsecureRequest warnings:
import requests
requests.packages.urllib3.disable_warnings()
import itertools, re, sys
from jira import JIRA
import random

from author import Authenticate  # no need to use as external command
from author import DoJIRAStuff

__version__ = "0.1"
thisFile = __file__

    
def main(argv):

    JIRASERVICE=""
    JIRAPROJECT=""
    JIRASUMMARY=""
    JIRADESCRIPTION=""
    PSWD=''
    USER=''
    jira=''
    
    parser = argparse.ArgumentParser(usage="""
    {1}    Version:{0}     -  mika.nokka1@gmail.com
    
    .netrc file used for authentication. Remember chmod 600 protection
    Creates issue for given JIRA service and project in JIRA
    Used to crate issue when build fails in Bamboo
    
    EXAMPLE: python {1}  -j http://jira.test.com -p BUILD -s "summary text"


    """.format(__version__,sys.argv[0]))

    parser.add_argument('-p','--project', help='<JIRA project key>')
    parser.add_argument('-j','--jira', help='<Target JIRA address>')
    parser.add_argument('-v','--version', help='<Version>', action='store_true')
    parser.add_argument('-s','--summary', help='<JIRA issue summary>')
    parser.add_argument('-d','--description', help='<JIRA issue description>')
    
    parser.add_argument('-x','--password', help='<JIRA password>')
    parser.add_argument('-u','--user', help='<JIRA user>')
    
    args = parser.parse_args()
        
    
    if args.version:
        print 'Tool version: %s'  % __version__
        sys.exit(2)    
         

    JIRASERVICE = args.jira or ''
    JIRAPROJECT = args.project or ''
    JIRASUMMARY = args.summary or ''
    JIRADESCRIPTION = args.description or ''
  
    PSWD= args.password or ''
    USER= args.user or ''
  
    # quick old-school way to check needed parameters
    if (JIRASERVICE=='' or  JIRAPROJECT=='' or JIRASUMMARY=='' or PSWD=='' or USER==''):
        parser.print_help()
        sys.exit(2)

    user, PASSWORD = Authenticate(JIRASERVICE,PSWD,USER)
    jira= DoJIRAStuff(user,PASSWORD,JIRASERVICE)
    #CreateIssue(jira,JIRAPROJECT,JIRASUMMARY,JIRADESCRIPTION,PSWD)
    CreateSimpleIssue(jira,JIRAPROJECT,JIRASUMMARY,JIRADESCRIPTION)
    

####################################################################################
def CreateIssue(ENV,jira,JIRAPROJECT,JIRASUMMARY,KEY,ISSUETYPE,ISSUETYPENW,STATUS,STATUSNW,PRIORITY,RESPONSIBLENW,RESPONSIBLE,INSPECTEDTIME,SHIP,SYSTEMNUMBERNW,SYSTEM,PERFORMERNW,DEPARTMENTNW,DEPARTMENT,DESCRIPTION,AREA,SURVEYOR,DECKNW,BLOCKNW,FIREZONENW):
    jiraobj=jira
    project=JIRAPROJECT

    
    print "Creating issue for JIRA project: {0}".format(project)
    

    issue_dict = {
    'project': {'key': JIRAPROJECT},
    'summary': JIRASUMMARY,
    'description': DESCRIPTION,
    'issuetype': {'name': ISSUETYPE},
    'priority': {'name': PRIORITY},
    
    'customfield_14613' if (ENV =="DEV") else 'customfield_14615' : str(SYSTEM),
    'customfield_14612' if (ENV =="DEV") else 'customfield_14603' : str(SHIP),
    'customfield_14607' if (ENV =="DEV") else 'customfield_14605' : str(PERFORMERNW),
    
    'customfield_10013' if (ENV =="DEV") else 'customfield_10013' : str(INSPECTEDTIME),
    'customfield_12900' if (ENV =="DEV") else 'customfield_12900' : str(KEY),
    'customfield_12906' if (ENV =="DEV") else 'customfield_12906' : str(RESPONSIBLENW),
    }

    #status

    try:
        new_issue = jiraobj.create_issue(fields=issue_dict)
        print "Issue created OK"
        print "Updating now all selection custom fields"

        # all custom fields could be objects with certain values for certain environments
        if (ENV =="DEV"):
                      
            print "Updating AREA"          
            if (AREA is None):
                new_issue.update(notify=False,fields={"customfield_10007":[ {"id": "-1"}]})  # multiple selection, see https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/
            else:
                new_issue.update(notify=False,fields={"customfield_10007": [{"value": AREA}]})
         
            print "Updating RESPONSIBLE"    
            if (RESPONSIBLE is None):
                new_issue.update(notify=False,fields={"customfield_10049": {"id": "-1"}})  # user selection, see https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/
            else:
                new_issue.update(notify=False,fields={"customfield_10049": {'name': RESPONSIBLE}})   
                
            CustomFieldSetter(new_issue,"customfield_14608" ,DEPARTMENTNW)    
            CustomFieldSetter(new_issue,"customfield_10010" ,DEPARTMENT)
           
            CustomFieldSetter(new_issue,"customfield_14606" ,STATUSNW)  
            CustomFieldSetter(new_issue,"customfield_14605" ,SYSTEMNUMBERNW)       
                    
            CustomFieldSetter(new_issue,"customfield_14604" ,ISSUETYPENW)
            CustomFieldSetter(new_issue,"customfield_14603" ,BLOCKNW)
            
            CustomFieldSetter(new_issue,"customfield_14601" ,DECKNW)
            CustomFieldSetter(new_issue,"customfield_14602" ,FIREZONENW)
            
                  
              
        elif (ENV =="PROD"):
            
            print "Updating AREA"          
            if (AREA is None):
                new_issue.update(notify=False,fields={"customfield_10007":[ {"id": "-1"}]})  # multiple selection, see https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/
            else:
                new_issue.update(notify=False,fields={"customfield_10007": [{"value": AREA}]})
         
            print "Updating RESPONSIBLE"    
            if (RESPONSIBLE is None):
                new_issue.update(notify=False,fields={"customfield_14430": {"id": "-1"}})  # user selection, see https://developer.atlassian.com/server/jira/platform/jira-rest-api-examples/
            else:
                new_issue.update(notify=False,fields={"customfield_14430": {'name': RESPONSIBLE}})   
                
            CustomFieldSetter(new_issue,"customfield_14606" ,DEPARTMENTNW)    
            CustomFieldSetter(new_issue,"customfield_10010" ,DEPARTMENT)
           
            CustomFieldSetter(new_issue,"customfield_14602" ,STATUSNW)  
            CustomFieldSetter(new_issue,"customfield_14613" ,SYSTEMNUMBERNW)       
                    
            CustomFieldSetter(new_issue,"customfield_14614" ,ISSUETYPENW)
            CustomFieldSetter(new_issue,"customfield_14612" ,BLOCKNW)
            
            CustomFieldSetter(new_issue,"customfield_14610" ,DECKNW)
            CustomFieldSetter(new_issue,"customfield_14611" ,FIREZONENW)
            
    
       
    
    
        print "Transit issue status"
        
        
        
        if (STATUS != "Todo"): # initial status after creation
            
            #map state to neede transit. Assunming WF supports thse transit (do for example admin only transit possibilty for migration)
            if (ENV=="DEV"):
                if (STATUS=="Closed"):
                    TRANSIT="CLOSED"
                if (STATUS=="Inspected"):
                    TRANSIT="INSPECTED"
            elif (ENV=="PROD"):
                if (STATUS=="Closed"):
                    TRANSIT="AUTOMATION_CLOSED"
                if (STATUS=="Inspected"):
                    TRANSIT="AUTOMATION_INSPECTED"
           
            
            print "Newstatus will be:{0}".format(STATUS)
            print "===> Executing transit:{0}".format(TRANSIT)
            jiraobj.transition_issue(new_issue, transition=TRANSIT)  # trantsit to state where it was in excel
        else:
            print "Initial status found: {0}, nothing done".format(STATUS)
    
    
    
    except Exception,e:
        print("Failed to create/use JIRA object, error: %s" % e)
        #print "Issue was:{0}".format(new_issue)
        sys.exit(1)
    return new_issue 

##################################################################################
# used only selection custom fields

def CustomFieldSetter(new_issue,CUSTOMFIELDNAME,CUSTOMFIELDVALUE):
    
    try:
    
        print "Trying update issue:{0}, field:{1}, value:{2}".format(new_issue,CUSTOMFIELDNAME,CUSTOMFIELDVALUE)
        if (CUSTOMFIELDVALUE is None or not CUSTOMFIELDVALUE): # None or "nothing" cases
            new_issue.update(notify=False,fields={CUSTOMFIELDNAME: {"id": "-1"}})
            print "Customfieldsetter: setting -1"
        else:    
            new_issue.update(notify=False,fields={CUSTOMFIELDNAME: {'value': CUSTOMFIELDVALUE}})            
        print "Issue:{0} field:{1} updated ok (value:{2})".format(new_issue,CUSTOMFIELDNAME,CUSTOMFIELDVALUE)    

    except Exception,e:
        print("Failed to UPDATE JIRA object, error: %s" % e)
        print "Issue was:{0}".format(new_issue)
        sys.exit(1)

############################################################################################'
# Quick way to create subtask
#
def CreateSubTask(ENV,jira,JIRAPROJECT,PARENT,SUBORIGINALREMARKEY,SUBSUMMARY,SUBISSUTYPENW,SUBISSUTYPE,SUBSTATUSNW,SUBSTATUS,SUBREPORTERNW,SUBCREATED,SUBDESCRIPTION,SUBSHIPNUMBER,SUBSYSTEMNUMBERNW,SUBPERFORMER,SUBRESPONSIBLENW,SUBASSIGNEE,SUBINSPECTION,SUBDEPARTMENTNW,SUBDEPARTMENT,SUBBLOCKNW,SUBDECKNW):
    jiraobj=jira
    project=JIRAPROJECT
 
    if (SUBSUMMARY==""):
        SUBSUMMARY="NA"
        
 
    print "Creating subtask for JIRA project: {0} Parent:{1}".format(project,PARENT)
    issue_dict = {
    'project': {'key': JIRAPROJECT},

    'summary': SUBSUMMARY,
    'description': SUBDESCRIPTION,
    'issuetype': {'name': SUBISSUTYPE}, #  is a Sub-task type CHANGE FOR target system
    'parent' : { 'id' : str(PARENT)},   # PARENT is an object, convert  SUBISSUETYPE


    'customfield_14612' if (ENV =="DEV") else 'customfield_14603' : str(SUBSHIPNUMBER),
    'customfield_14607' if (ENV =="DEV") else 'customfield_14605' : str(SUBPERFORMER),
    'customfield_14615' if (ENV =="DEV") else 'customfield_14616' : str(SUBREPORTERNW),
    
    'customfield_10013' if (ENV =="DEV") else 'customfield_10013' : str(SUBINSPECTION),
    'customfield_14609' if (ENV =="DEV") else 'customfield_14607' : str(SUBCREATED),
    'customfield_14614' if (ENV =="DEV") else 'customfield_14609' : str(SUBORIGINALREMARKEY),
    'customfield_12906' if (ENV =="DEV") else 'customfield_12906' : str(SUBRESPONSIBLENW), 


    }



    #status

    try:
        
        
        new_issue = jiraobj.create_issue(fields=issue_dict)
        print "Subtask created OK"
        print "Updating now all selection custom fields"

        
        # all custom fields could be objects with certain values for certain environments
        if (ENV =="DEV"):
                      
            print "Updating SUBTASK ASSIGNEE" 
            new_issue.update(assignee={'name': SUBASSIGNEE})        
                   
            CustomFieldSetter(new_issue,"customfield_14604" ,SUBISSUTYPENW)
            CustomFieldSetter(new_issue,"customfield_14606" ,SUBSTATUSNW) 
            CustomFieldSetter(new_issue,"customfield_14605" ,SUBSYSTEMNUMBERNW)     
            CustomFieldSetter(new_issue,"customfield_14608" ,SUBDEPARTMENTNW) 
            CustomFieldSetter(new_issue,"customfield_10010" ,SUBDEPARTMENT)
            CustomFieldSetter(new_issue,"customfield_14603" ,SUBBLOCKNW)
            CustomFieldSetter(new_issue,"customfield_14601" ,SUBDECKNW)
            
        elif (ENV =="PROD"):
            
            print "Updating SUBTASK ASSIGNEE" 
            new_issue.update(assignee={'name': SUBASSIGNEE})        
                   
            CustomFieldSetter(new_issue,"customfield_14614" ,SUBISSUTYPENW)
            CustomFieldSetter(new_issue,"customfield_14602" ,SUBSTATUSNW) 
            CustomFieldSetter(new_issue,"customfield_14613" ,SUBSYSTEMNUMBERNW)     
            CustomFieldSetter(new_issue,"customfield_14606" ,SUBDEPARTMENTNW) 
            CustomFieldSetter(new_issue,"customfield_10010" ,SUBDEPARTMENT)
            CustomFieldSetter(new_issue,"customfield_14612" ,SUBBLOCKNW)
            CustomFieldSetter(new_issue,"customfield_14610" ,SUBDECKNW)
            
    
       
    
    
        print "Transit issue status"
        
        
        
        if (SUBSTATUS != "Open" ): # initial status after creation
            
            #map state to neede transit. Assunming WF supports thse transit (do for example admin only transit possibilty for migration)
            #if (SUBSTATUS=="Closed"):
            #    TRANSIT="CLOSED"
            #if (SUBSTATUS=="Inspected"):
            #    TRANSIT="INSPECTED"
           
            #subtask state transits from initla state, cahgen accorging real WF
            if (ENV=="DEV"):
                if (SUBSTATUS=="open"):
                    TRANSIT="OPEN"
                if (SUBSTATUS=="resolved"):
                    TRANSIT="RESOLVED"
            elif (ENV=="PROD"):
                if (SUBSTATUS=="open"):
                    TRANSIT="AUTOMATION_OPEN"
                if (SUBSTATUS=="resolved"):
                    TRANSIT="AUTOMATION_RESOLVED"
            
            
            print "Subtask newstatus will be:{0}".format(SUBSTATUS)
            print "===> Executing transit:{0}".format(TRANSIT)
            jiraobj.transition_issue(new_issue, transition=TRANSIT)  # trantsit to state where it was in excel
        else:
            print "Initial status found: {0}, nothing done".format(STATUS)
    


    
        
    except Exception,e:
        print("Failed to create JIRA object, error: %s" % e)
        sys.exit(1)
    return new_issue 

########################################################################################
# test creating issue with multiple selection list custom field
def CreateSimpleIssue(jira,JIRAPROJECT,JIRASUMMARY,JIRADESCRIPTION):
    #jiraobj=jira
    project=JIRAPROJECT
    
    
    #lottery = random.randint(1,3)
    #if (lottery==1):
    #    TASKTYPE="Steal"
    #elif (lottery>1):
    #    TASKTYPE="Outfitting"
    #else:
    #    TASKTYPE="Task"
    
    #TASKTYPE="Hull Inspection NW"
    TASKTYPE="Task"
    
    print "Creating issue for JIRA project: {0}".format(project)
    

    
    issue_dict = {
    'project': {'key': JIRAPROJECT},
    'summary': str(JIRASUMMARY),
    'description': str(JIRADESCRIPTION),
    'issuetype': {'name': TASKTYPE},
    'customfield_14600' : [{'value': str("cat")},{'value': str("bear")}] ,
    }

    try:
        new_issue = jira.create_issue(fields=issue_dict)
        print "Issue created OK"
    except Exception,e:
        print("Failed to create JIRA object, error: %s" % e)
        sys.exit(1)
    return new_issue 



        
if __name__ == "__main__":
        main(sys.argv[1:])
        
        
        
        
        