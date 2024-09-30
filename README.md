# pyclone
Python script to interact with GoClone
```
usage: pyclone.py [-h] -u USERNAME -p PASSWORD -a {bulk_clone,delete,view,refresh,revert,power} [-t TEMPLATE] [-l USERLIST] [-snapshot SNAPSHOT]
                  [-state {on,off}] [-r {pods,templates}]

Script for cloning pods

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username
  -p PASSWORD, --password PASSWORD
                        Password
  -a {bulk_clone,delete,view,refresh,revert,power}, --action {bulk_clone,delete,view,refresh,revert,power}
                        Action to perform

pod_operations:
  Arguments for bulk_clone, delete, revert, and power

  -t TEMPLATE, --template TEMPLATE
                        Template name for bulk cloning
  -l USERLIST, --userlist USERLIST
                        Path to userlist file for bulk cloning

power:
  Additional arguments for revert

  -snapshot SNAPSHOT, --snapshot SNAPSHOT
                        Snapshot name to revert to

power:
  Additional arguments for power operations

  -state {on,off}, --state {on,off}
                        Power status to set

view:
  Arguments for viewing resources

  -r {pods,templates}, --resource {pods,templates}
                        Resource to view
```
Example:
```
python .\pyclone.py -u admin -p password -a view -r templates

[+] Login Response:  {"message":"Successfully logged in!"}
[+] Preset templates
        CPTCTryouts2024
        Telemetry_Test
[+] Images available for custom templates
        Linux:
                Debian 12 Blank     
        Windows:
                Windows Server 2008 R2 Blank
        Networking:
                VyOS_PodRouter

python .\pyclone.py -u user -p password -a bulk_clone -l .\userlist.txt -t Telemetry_Test
```
