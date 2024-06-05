import bibtexparser


with open('ArticleList_170115.bib') as bibtex_file:
     bibtex_str = bibtex_file.read()

bib_database = bibtexparser.loads(bibtex_str)
sortedentries = sorted(bib_database.entries, key=lambda k: k['year'] if 'year' in k else '0',reverse=True) 

f = open('tstinfo.json', 'w')
f.write("""{\n"_comment": "publication graphics should be 250 x 125 ",\n"_comment": " Available Tags: qbio, Theory" ,\n"_comment": {"auth":"","url":"","title":"","ref":"","img":""},\n"pubs": [\n""")
for entry in sortedentries:
    if(entry['ENTRYTYPE']=='article'):
        titlestr=entry['title'].replace("\\","")
        print(titlestr)
    
        authnames=list(map(lambda x: x.strip(),entry['author'].split(' and ')))
        authstr=''
        for author in authnames:
            tauthor=list(map(lambda x: x.strip(),author.split(',')))
            if(len(tauthor)==2):
                authstr+=tauthor[1]+' '+tauthor[0]+', '
            else:
                authstr+=','+tauthor[0]
        authstr=authstr.strip(', ')
        authstr=authstr.replace("""{\\'c}""",'c')
        print(authstr)
    
        refstr=''
        if('journal' in entry):
            refstr+=entry['journal'] + ' '
            if('number' in entry):
                refstr+=entry['number']
            refstr+=', '
            if('pages' in entry):
                refstr+=entry['pages'].replace('--','-') + ' '
            if('year' in entry):
                refstr+=entry['year']
                
        f.write('\t{')
        f.write('"auth":"'+authstr+'"')
        f.write(',')
        f.write('"title":"'+titlestr+'"')
        f.write(',')
        f.write('"ref":"'+refstr+'"')
        f.write('},\n')
f.write(']\n}')
f.close()