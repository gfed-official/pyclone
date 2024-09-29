# pyclone
Python script to interact with GoClone
```
usage: pyclone.py [-h] -u USERNAME -p PASSWORD -a {clone,bulk_clone,delete,view,refresh} [-t TEMPLATE] [-l USERLIST] [-r {pods,templates}]

Script for cloning pods

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username
  -p PASSWORD, --password PASSWORD
                        Password
  -a {clone,bulk_clone,delete,view,refresh}, --action {clone,bulk_clone,delete,view,refresh}
                        Action to perform
  -t TEMPLATE, --template TEMPLATE
                        Template name
  -l USERLIST, --userlist USERLIST
                        Path to userlist file
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
