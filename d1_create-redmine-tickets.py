'''
d1_create-redmine-tickets.py

Author: Monica Ihli

Date: 2/6/2018

Dependencies/Requirements:
  - tickets-template.xml must be in the same directory.
  - Make sure correct PROJECT_ID is set
  - API Key must be saved to 'api-key.txt' with no extra spaces or newlines.
  - Expects that you have already created a main MNDeployment issue for this node (customer). The MNDeployment ticket
    is the main parent ticket upon which all other issues for that node are anchored.
  - Tested with Python 3.3.5 and python-redmine v 2.0.2
  
How to Use:
  - You will be asked for the issue number of that MNDeployment ticket.
  - You will be asked to provide a short abbreviated name form or acronym which can be appended to the beginning of the
    title for every ticket created for that node. This prevents us from having to deal with, for example, a bunch of
    tickets that have the same title. So instead of "Move to Production" as a story ticket subject, it would say
    something like "LTER - Move to Production" if you entered "LTER" for that prompt.
'''



import xml.etree.ElementTree as ET
from redminelib import Redmine
from redminelib.exceptions import ResourceNotFoundError, AuthError


f = open ('api-key.txt', 'r')
API_KEY = f.readlines()
REDMINE_URL = 'https://redmine.dataone.org'
redmine = Redmine(REDMINE_URL, key=API_KEY)
PROJECT_ID = '20' # 20 is the real MN project id. 45 is the test MN project id
TEMPLATE_PATH = "./tickets-template.xml"


def main():
  parent_id = get_main_deployment_ticket()
  node_abbrev = input('Enter an acronym or abbreviated form of node name to prefix new ticket subjects with: ')
  while True:

    print('\nThe current ticket structure for this Member Node Deployment is as follows:')
    print('(Nothing will display here if there are no child tickets yet.')
    display_mn_issue_structure(parent_id)
    input('\nPress enter to continue. ')
    choice = display_options()
    add_new_issues(parent_id, choice, node_abbrev, TEMPLATE_PATH)
    choice = input('\nAdd more issues? Please enter Y or N: ')
    if choice == 'Y':
      pass
    elif choice == 'N':
      break
    else:
      print('Well, "{}" isn\'t a "Y", so I\'m ending this program anyways.'.format(choice))
      break
  print('Goodbye!')
  input('Press Enter to end the program.')



def get_main_deployment_ticket():
  """This program assumes that you have already created the main MNDeployment parent ticket for this node. In this
  function, you are asked to provide the issue number for that parent ticket. It will pull information about that issue
  and ask you to confirm if this is the issue you meant to specify. If not,
  will continously loop through until (a) valid issue # is provided and (b) user
  indicates this number retrieved correct issue.
  """
  while True:
    try:
      parent_id = input('\nPlease enter the issue # for a MNDeployment ticket you wish to add tasks to: ')
      parent_issue = redmine.issue.get(parent_id)  # get the full issue details
      print('\nYou selected {} #{}: {}'.format(
        parent_issue['tracker']['name'], parent_issue['id'], parent_issue['subject']))
      response = input('Is this the correct ticket? Enter Y or N: ')
      if response == 'Y':
        return(parent_id)
    except ResourceNotFoundError:
      print('\nInvalid issue number. Try again.\n')


def display_mn_issue_structure(parent_id):
  ''' Function which prints ticket number and subject for all child issues nested within main deployment ticket.
  This is a recursive function. It starts by getting called origional parent deployment ticket. For all children
  of the currently examined ticket, the function calls itself.
  will continuously loop through option selection until an entry is 
  confirmed by the user. Note that for the moment there is no input validation
  enforce a valid choice '''
  parent_issue = redmine.issue.get(parent_id, include='children')  # get the full issue details
  if parent_issue['tracker']['name'] == 'Task':
    print(
      "\t" + parent_issue['tracker']['name'] + ' # ' + str(parent_issue['id']) + ' - ' + parent_issue['subject'])
  elif parent_issue['tracker']['name'] == 'MNDeployment':
    pass # Don't repeat printing parent deployment ticket name. n)
  else:
    print(parent_issue['tracker']['name'] + ' # ' + str(parent_issue['id']) + ' - ' + parent_issue['subject'])
  for child_issue in parent_issue.children._resources:
    display_mn_issue_structure(child_issue['id'])

def display_options():
  choices={'1': '(1) Story: Discovery', '2': '(2) Story: Planning', '3': "(3) Story: Testing & Development",
           '4': '(4) Move to Production'}
  options_str = '(1) Story: Discovery\n' + \
                '\tTask: Initial Communications\n' + \
                '\tTask: Feasibility Assessment\n' + \
                '\n(2) Story: Planning\n' + \
                '\tTask: MN Communications\n' + \
                '\tTask: Technical Requirements\n' + \
                '\tTask: Training & Education\n' + \
                '\tTask: Metadata Validation\n' + \
                '\n(3) Story: Testing & Development\n' + \
                '\tTask: Develop or Implement MN Software\n' + \
                '\tTask: Test Registration\n' + \
                '\tTask: Display as Upcoming\n' + \
                '\n(4) Story: Move to Production\n' + \
                '\tTask: Implement in Production\n' + \
                '\tTask: Register in Production\n' + \
                '\tTask: Mutual Acceptance\n' + \
                '\tTask: Formal Announcement\n\n'

  while True:
    print('\nThe following sets of Stories + Task are available to be added to this ticket:\n')
    print(options_str)
    choice = input('\nPlease enter an option 1-4 for the stories/tasks you wish to add to this node: ')
    print('You selected: {}'.format(choices[choice]))
    verify = input('Proceed with generating tickets? Y or N: ')
    if verify == 'Y':
      return choice
    elif verify == 'N':
      pass
    else:
      input('Invalid response. Press enter to try again.')



def add_new_issues(parent_id, choice, node_abbrev, template_path):
  '''
  The file tickets-template.xml must be in the same directory as this script. It lays
  out a series of stories each with several tasks nested within. This function will
  read the entire template, then use portions of it to populate tickets based on the
  user's selection, which has been passed as the "choice" parameter. Assumes
  a parent-child, 1:N relationship between stories and tickets.
  '''
  root = ET.parse("tickets-template.xml")
  choices_dict = {'1': 'Discovery', '2': 'Planning', '3': 'Testing', '4': 'Production'}
  story = root.find('.//story[@name="%s"]' % choices_dict[choice])
  issue = redmine.issue.new()
  issue.project_id = PROJECT_ID
  issue.tracker_id = '4'  # 4 is story
  issue.subject = node_abbrev + ': ' + story.find('subject').text
  issue.description = story.find('desc').text
  issue.parent_issue_id = parent_id
  issue.save()
  print('Created Story #{}- {}'.format(issue.id, issue.subject))
  story_id = issue.id
  for task in story.findall('./tasks/task'):
    issue = redmine.issue.new()
    issue.project_id = PROJECT_ID
    issue.tracker_id = '5'  # 5 is task
    issue.subject = node_abbrev + ': ' + task.find('subject').text
    issue.description = task.find('desc').text
    issue.parent_issue_id = story_id
    issue.save()
    print('Created Task #{} - {}'.format(issue.id, issue.subject))


if __name__ == "__main__":
  main()



