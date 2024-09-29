import argparse
import requests
import sys
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib.parse

# Constants
URL = "https://kamino.calpolyswift.org/api/v1"
RSR = ["pods", "templates"]
# Initialize session
session = requests.Session()
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Log in and set the cookie. Params are self explanatory
def login(username: str, password: str):
    response = session.post(f"{URL}/login", json={"username": username, "password": password}, verify=False)
    print("[+] Login Response: ", response.text)
    response.raise_for_status()

# Clone a single pod under current context. You probably are never gonna call this
def single_clone(template: str):
    headers = {'Content-Type': 'application/json'}
    response = session.post(f"{URL}/pod/clone/template", json={"template": template}, headers=headers, cookies=session.cookies.get_dict(), verify=False)
    print("[+]", response.text)
    response.raise_for_status()

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
    response.raise_for_status()

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
    delete_response.raise_for_status()

# View a resource
# Only pod and template viewing is supported right now
def view(resource: str):
    if resource == "pods":
        response = session.get(f"{URL}/admin/view/pods", cookies=session.cookies.get_dict(), verify=False)
        pods     = json.loads(response.text)
        print("[+] Active user pods:")
        for pod in pods:
            print("\t" + pod["Name"])
        response.raise_for_status()
    elif resource == "templates":
        response = session.get(f"{URL}/view/templates/preset", cookies=session.cookies.get_dict(), verify=False)
        presets  = json.loads(response.text)
        print("[+] Preset templates")
        for preset in presets["templates"]:
            print("\t" + preset)
        response.raise_for_status()

        print("[+] Images available for custom templates")
        response  = session.get(f"{URL}/view/templates/custom", cookies=session.cookies.get_dict(), verify=False)
        templates = json.loads(response.text)
        for category in templates["templates"]:
            print("\t" + category['name'] + ":")
            for vm in category['vms']:
                print("\t\t" + urllib.parse.unquote((urllib.parse.unquote(vm)))) # Idk bro it just made it work
        response.raise_for_status()
    return
    
# Refresh templates and their snapshots
def refresh():
    response = session.post(f"{URL}/admin/templates/refresh", cookies=session.cookies.get_dict(), verify=False)
    response.raise_for_status()
    return

def main():
    parser = argparse.ArgumentParser(description="Script for cloning pods")
    parser.add_argument('-u', '--username', required=True, help="Username")
    parser.add_argument('-p', '--password', required=True, help="Password")
    parser.add_argument('-a', '--action', required=True, choices=['clone', 'bulk_clone', 'delete', 'view', 'refresh'], help="Action to perform")
    parser.add_argument('-t', '--template', help="Template name")
    parser.add_argument('-l', '--userlist', help="Path to userlist file")
    parser.add_argument('-r', '--resource', help="Resource to view", choices=RSR)

    args = parser.parse_args()

    if args.action in ['clone', 'bulk_clone'] and not args.template:
        print("[!] Need to specify a template to clone!")
        return
    
    if args.action == "delete" and not args.userlist and not args.template:
        print("[!] Need to specify a userlist or a template for deletion")
        return
    
    if args.action == 'bulk_clone' and not args.userlist:
        print("[!] Need to specify a userlist for bulk cloning!")
        return

    if args.action == 'view' and not args.resource:
        print("[!] Need to specify resource to view!")
        return

    login(username=args.username, password=args.password)

    if args.action == 'clone':
        single_clone(args.template)
    elif args.action == 'bulk_clone':
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
if __name__ == "__main__":
    main()
