'''
mn-updates-report.py

Author: Monica Ihli
Date: 2/6/2018
Dependencies: Tested with python-redmine v 2.0.2
Additional Requirements: A wiki page must have been created for pushing the report information to.

Configuration Changes: Set the REDMINE_URL and API_KEY values as needed. API Key can be found under My Account
in redmine. Wiki page to send updates to is specified at the end of main() in redmine.wiki_page.update(). The # of days
worth of update notes to check for can be altered in get_latest_updates()

This program cycles through all top-level issues in a project which have a particular tracker_id. The top-level issue is
checked for updates containing notes, and any sub-issues and their children as well. Recent updates (within the last 7
 days) are assembled into a unicode string which is finally pushed as an update to a wiki page. Note that the
 information is formatted to stylize the report for presentation in the redmine wiki page, using redmine
 formatted headers, bold, italics, etc.
'''

from redminelib import Redmine
from redminelib.exceptions import AuthError
import datetime

API_KEY = 'asdf'
REDMINE_URL = 'https://redmine.dataone.org'

redmine = Redmine(REDMINE_URL, key=API_KEY)
report_str = u''

def main():
  global report_str

  status_list = [{'id': 12, 'name': 'PLANNING'},
                 {'id': 7, 'name': 'TESTING'},
                 {'id': 9, 'name': 'OPERATIONAL'}]

  for status in status_list:
    # project_id 9 is 'Member Nodes', tracker_id 9 is 'MNDeployment'
    issues = redmine.issue.filter(project_id='20', tracker_id='9', status_id=status['id'])
    report_str += '\n# **Nodes in {} Status**\n'.format(status['name'])
    report_str += '\n' + '-' * 50 + '\n'

    for member_node_issue in issues: # for every parent MN issue returned from the query
      updates_str = get_ticket(id=member_node_issue['id'], updates_str=u'') # in beginning, updates string is empty
      if len(updates_str) > 0: # will not include this MN in the report if no updates to share.
        report_str += '\n## **' + member_node_issue['subject'] + '**\n'
        report_str += '**Start Date**: ' + datetime.datetime.strftime(member_node_issue.start_date, '%Y-%m-%d') + '\n'
        report_str += '**Assigned to**: ' + str(member_node_issue['assigned_to']) + '\n'
        report_str += '**Recent Updates**:\n'
        report_str += updates_str
        report_str += '\n'
        report_str += '\n' + '-' * 50 + '\n\n'

  try:
    redmine.wiki_page.update('Latest_updates',
                             project_id=20,
                             text=report_str)
  except AuthError:
    print 'Authorization error. Check for valid api key.'
  except Exception, e:
    print e

def get_ticket(id, updates_str):
  parent_issue = redmine.issue.get(id, include='children,journals')  # get the full issue details
  source_str = '\n### ***From Ticket #' + str(parent_issue['id']) + ' - ' + parent_issue['subject'] + '***\n'
  updates_str = get_latest_updates(parent_issue, source_str, updates_str)
  for child_issue in parent_issue.children._resources:
    updates_str = get_ticket(child_issue['id'], updates_str)
  return updates_str

def get_latest_updates(issue_details, source_str, updates_str):
  source_printed = 0
  for update in issue_details.journals._resources:
    if ((datetime.datetime.now() - datetime.datetime.strptime(update['created_on'], '%Y-%m-%dT%H:%M:%SZ')).days < 8):
      if len(update['notes']) > 1: # because not interested in updates that don't include notes
        if source_printed == 0:
          updates_str += source_str
          source_printed = 1
        datestr = datetime.datetime.strftime(
          datetime.datetime.strptime(update['created_on'], '%Y-%m-%dT%H:%M:%SZ'), '%Y-%m-%d')
        updates_str += '*On ' + datestr + ' by ' + update['user']['name'] + ':\n' + update[u'notes']
  return updates_str

if __name__ == '__main__':
  main()
