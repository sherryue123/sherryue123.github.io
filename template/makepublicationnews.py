import json
import re
from pprint import pprint

with open('publications.json') as json_data:
    pubs = json.load(json_data)["pubs"]
    json_data.close()

with open('people.json') as json_data:
    studs = json.load(json_data)["Students"]
    json_data.close()

for pub in pubs:
    fullstr=""
    authors=[]
    for student in studs:
        if ((student["FirstName"] in pub["auth"])and (student["LastName"] in pub["auth"])):
            authors.append(student["FirstName"] + " " + student["LastName"])
    if len(authors)==0:
        break
    if len(authors)==1:
        fullstr+="Congratulations to " + authors[0]
    if len(authors)>1:
        fullstr+="Congratulations to "
        for jj in range(len(authors)-1):
            fullstr+= authors[jj]+", "
        fullstr+= "and " + authors[-1]
    
    fullstr+=" for the paper "

    if 'url' in pub:
        fullstr+="""<a href=\""""+pub['url']+"""\">\""""+pub['title']+"""\"</a>"""
    else:
        fullstr+=pub['title']
    m = re.search("\d", pub['ref'])
    if( not m):
        journal=pub['ref']
    else:
        journal=pub['ref'][:m.start()]
        
    fullstr+=" published in " + journal + "."
    
    print(fullstr)