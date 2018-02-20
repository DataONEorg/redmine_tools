# redmine_tools
Tools used by the DataONE project for interacting with redmine.
These tools use the python-redmine library documented at https://python-redmine.com/. 


### d1_mn-updates-report.py

Tested with Python 3.3.5 and python-redmine v 2.0.2

To simplify keeping track of recent updates across numerous project issues and their child issues, this tool creates a report of any new notes added to top-level issues or their children within the MN Project. Top-level issues (with tracking name 'MNDeployment') serve as the primary record of a member, to which all other issues about that member are attached. These other issues will include Stories (descriptions of very broad milestones to be achieved as part of deploying a new member node) and Tasks within Stories (more specific information about steps that should be accomplished as part of the Story). Later on, additional Tasks may be added for such reasons as needing to upgrade software or providing technical support.

The report is organized so that any new notes added to a MNDeployment ticket, or it's child Stories or Tasks, within the last 7 days will be included. Who added the note, in which issue, and when is also displayed. The information is pushed to a page in the project wiki, and marked up appropriately for display in redmine. Updating the report can be run on demand, or scheduled to occur as frequently as needed with a cron entry to run the script. Example output can be found at the current target wiki page: https://redmine.dataone.org/projects/mns/wiki/Latest_updates


### MN-Updates-Report_executable.zip
A zip file containing an executable version of d1_mn-updates-report with supporting files, for use on Windows 10.  Generated with py2exe.  The target wiki page for updates is hardcoded and so a new executable would need to be generated to change the page. Before running, edit the api-key.txt file and replace the text with your redmine API key.
