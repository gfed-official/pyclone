import argparse
import requests
import sys
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib.parse

# Constants
URL = "https://goclone-dev.sdc.cpp/api/v1"
RSR = ["pods", "templates"]
# Initialize session
session = requests.Session()
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Log in and set the cookie. Params are self explanatory
def login(username: str, password: str):
    response = session.post(f"{URL}/login", json={"username": username, "password": password}, verify=False)
    print("[+] Login Response: ", response.text)
    print(response.text)

# Clone a single template across all users of a newline separated userlist. This is probably gonna be used most often
def bulk_clone(template: str, userlist: str):
    headers = {'Content-Type': 'application/json'}
    users   = []
    with open(userlist, 'r') as f:
        for line in f:
            users.append(line.strip())
    data = {"template": template, "users": users}
    response = session.post(f"{URL}/admin/pod/clone/bulk", json=data, headers=headers, cookies=session.cookies.get_dict(), verify=False)
    print(response.text)

# Delete pods. 
# This function assumes the template name passed is a template. There is no validation for arbitrary strings (lol)
# If ONLY template is defined, it deletes all instances of that template
# If ONLY userlist is defined, it deletes all pods from that user
# If both are defined, it deletes all pods from that template of that user
def delete(template: str = "", userlist: str = ""):
    headers = {'Content-Type': 'application/json'}
    response = session.get(f"{URL}/admin/view/pods", cookies=session.cookies.get_dict(), verify=False)
    pods = response.json()

    # Deletion by userlist
    if len(template) > 0 and len(userlist) == 0:
        delete_response = session.delete(f"{URL}/admin/pod/delete/bulk", cookies=session.cookies.get_dict(), verify=False, json={"filters": [template]})
        print(delete_response.text)
    
    # Deletion by template
    elif len(userlist) > 0 and len(template) == 0:
        users = []
        with open(userlist, 'r') as f:
            for line in f:
                users.append(line.strip())
        delete_response = session.delete(f"{URL}/admin/pod/delete/bulk", cookies=session.cookies.get_dict(), verify=False, json={"filters": users})
        print(delete_response.text)
    # Deletion by userlist and template
    else:
        pods = []
        with open(userlist, 'r') as f:
            for line in f:
                pods.append(template + "_" + line.strip())
        print({"filters": pods})
        delete_response = session.delete(f"{URL}/admin/pod/delete/bulk", cookies=session.cookies.get_dict(), verify=False, json={"filters": pods})
        print(delete_response.text)

# View a resource
# Only pod and template viewing is supported right now
def view(resource: str):
    if resource == "pods":
        response = session.get(f"{URL}/admin/view/pods", cookies=session.cookies.get_dict(), verify=False)
        pods     = json.loads(response.text)
        print("[+] Active user pods:")
        for pod in pods:
            print("\t" + pod["Name"])
        if response.status_code != 200:
            print(response.text)
    elif resource == "templates":
        response = session.get(f"{URL}/view/templates/preset", cookies=session.cookies.get_dict(), verify=False)
        presets  = json.loads(response.text)
        print("[+] Preset templates")
        for preset in presets["templates"]:
            print("\t" + preset)
        if response.status_code != 200:
            print(response.text)

        print("[+] Images available for custom templates")
        response  = session.get(f"{URL}/view/templates/custom", cookies=session.cookies.get_dict(), verify=False)
        templates = json.loads(response.text)
        for category in templates["templates"]:
            print("\t" + category['name'] + ":")
            for vm in category['vms']:
                print("\t\t" + urllib.parse.unquote((urllib.parse.unquote(vm)))) # Idk bro it just made it work
        if response.status_code != 200:
            print(response.text)
    return
    
# Refresh templates and their snapshots
def refresh():
    response = session.post(f"{URL}/admin/templates/refresh", cookies=session.cookies.get_dict(), verify=False)
    print(response.text)
    return

# Modify the power state of pods
def power(template: str, userlist: str, state: str):
    headers = {'Content-Type': 'application/json'}
    pods = []
    with open(userlist, 'r') as f:
        for line in f:
            pods.append(template + "_" + line.strip())
    print({"filters": pods})
    on = True if state == "on" else False
    response = session.post(f"{URL}/admin/pod/power/bulk", cookies=session.cookies.get_dict(), verify=False, json={"filters": pods, "On": on})
    print(response.text)
    return

# Revert Pods to a snapshot name
def revert(template: str, userlist: str, snapshot: str):
    headers = {'Content-Type': 'application/json'}
    pods = []
    with open(userlist, 'r') as f:
        for line in f:
            pods.append(template + "_" + line.strip())
    print({"filters": pods})
    response = session.post(f"{URL}/admin/pod/revert/bulk", cookies=session.cookies.get_dict(), verify=False, json={"filters": pods, "snapshot": snapshot})
    print(response.text)
    return

def main():
    parser = argparse.ArgumentParser(description="Script for cloning pods")
    parser.add_argument('-u', '--username', required=True, help="Username")
    parser.add_argument('-p', '--password', required=True, help="Password")
    parser.add_argument('-a', '--action', required=True, choices=['bulk_clone', 'delete', 'view', 'refresh', 'revert', 'power'], help="Action to perform")

    pod_operations = parser.add_argument_group('pod_operations', 'Arguments for bulk_clone, delete, revert, and power')
    pod_operations.add_argument('-t', '--template', help="Template name for bulk cloning")
    pod_operations.add_argument('-l', '--userlist', help="Path to userlist file for bulk cloning")

    revert_args = parser.add_argument_group('power', 'Additional arguments for revert')
    revert_args.add_argument('-snapshot', '--snapshot', help="Snapshot name to revert to")

    power_args = parser.add_argument_group('power', 'Additional arguments for power operations')
    power_args.add_argument('-state', '--state', choices=["on", "off"], help="Power status to set")

    view_group = parser.add_argument_group('view', 'Arguments for viewing resources')
    view_group.add_argument('-r', '--resource', help="Resource to view", choices=RSR)

    args = parser.parse_args()

    if args.action == 'bulk_clone' and not args.template and not args.userlist:
        print("[!] Need to specify a template and userlist for bulk_clone!")
        return
    
    if args.action in ["delete", "revert"] and not args.userlist and not args.template:
        print("[!] Need to specify a userlist or a template for this operation")
        return

    if args.action == "revert" and not args.snapshot:
        print("[!] Need to specify snapshot to revert to!")
        return  

    if args.action == "power" and not args.state:
        print("[!] Need to specify power state to set!")
        return  
    
    if args.action == "power" and (not args.userlist or not args.template) :
        print("[!] Need to specify a userlist and a template for this operation")
        return
    
    if args.action == 'view' and not args.resource:
        print("[!] Need to specify resource to view!")
        return

    login(username=args.username, password=args.password)

    if args.action == 'bulk_clone':
        bulk_clone(args.template, args.userlist)
    elif args.action == 'delete':
        if args.template is not None and args.userlist is None:
            delete(template=args.template)
        elif args.template is None and args.userlist is not None:
            delete(userlist=args.userlist)
        elif args.template is not None and args.userlist is not None:
            delete(template=args.template, userlist=args.userlist)
    elif args.action == 'view':
        if args.resource in RSR:
            view(args.resource)
        else:
            print("[!] Only viewing", RSR, "is implemented")
    elif args.action == 'refresh':
        refresh()
    elif args.action == 'power':
        power(template=args.template, userlist=args.userlist, state=args.state)
    elif args.action == 'revert':
        revert(template=args.template, userlist=args.userlist, snapshot=args.snapshot)
if __name__ == "__main__":
    main()
