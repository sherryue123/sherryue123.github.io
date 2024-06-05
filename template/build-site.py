__author__ = 'Jonathan Simon'

from css_html_js_minify import html_minify  #, css_minify
import jinja2, json, re
from math import ceil
import datetime
from csscompressor import compress
import sys,getopt,os.path
import operator
from PIL import Image
from resizeimage import resizeimage
import datetime

templateLoader = jinja2.FileSystemLoader(searchpath=['','template/'])
env = jinja2.Environment(loader=templateLoader)


def render_template(name, vars):
    html = env.get_template(name).render(vars)
    return html

def GenerateSiteMap(list,output,rebuild):
	newmap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset\n     xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n     xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n         http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n'
	newmap=newmap+'<url>\n     <loc>http://simonlab.uchicago.edu/</loc>\n     <changefreq>weekly</changefreq>\n     <priority>1.00</priority>\n</url>\n'
	for page in list:
		mydatetime = datetime.datetime.strptime(page['date'],'%B %d, %Y')
		mydate = mydatetime.strftime('%Y-%m-%d')
		
		priority=1.0
		if not page['name'] in ['index.html']:
			priority=.8**(page['name'].count('/')+1)
		if page['name'] in ['news.html','index.html','publications.html']:
			freq='weekly'
		else:
			freq='monthly'
		if page['name'] not in ['404.html']:
			newmap=newmap+'<url>\n     <loc>http://simonlab.uchicago.edu/' + page['name'] + '</loc>\n     <lastmod>'+mydate+'</lastmod>\n     <changefreq>'+freq+'</changefreq>\n     <priority>'+("{:.2f}".format(priority)) +'</priority>\n</url>\n'
	newmap=newmap+'</urlset>\n'
	
	if not rebuild:
		try:
			with open(output, 'r') as f:
				oldmap = f.read();
		except (OSError, IOError) as e:
			oldmap='xxxx'
		if newmap != oldmap:
			with open(output, 'w') as f:
				f.write(newmap)
			print('wrote '+output)
	else:
		with open(output, 'w') as f:
			f.write(newmap)
		print('wrote '+output)
	return newmap

def minify_css_to_output(name, output, rebuild):
	with open(name, 'r') as f:
		newcss = f.read();
	newcss=compress(newcss);
#	newcss=css_minify(newcss);  #commented out to save 3 seconds per run -- 50% of overall time.
	if not rebuild:
		try:
			with open(output, 'r') as f:
				oldcss = f.read();
		except (OSError, IOError) as e:
			oldcss='xxxx'
		if newcss != oldcss:
			with open(output, 'w') as f:
				f.write(newcss)
			print('wrote '+output)
	else:
		with open(output, 'w') as f:
			f.write(newcss)
		print('wrote '+output)

	return newcss

def render_template_to_output(name, vars, output, rebuild):
	html = render_template(name, vars)
	html = html_minify(html)
	if not rebuild:
		try:
			with open(output, 'r') as f:
				oldhtml = f.read();
		except (OSError, IOError) as e:
			oldhtml='xxxx'
		UndatedOldHtml=re.sub(r'<span id=\"?UpdateTime\"? ?>[a-zA-Z 0-9,]* </span>','',oldhtml)
		UndatedHtml=re.sub(r'<span id=\"?UpdateTime\"? ?>[a-zA-Z 0-9,]* </span>','',html)
		if UndatedOldHtml != UndatedHtml:
			with open(output, 'w') as f:
				f.write(html)
			print('wrote '+output)
			match=re.search(r'<span id=\"?UpdateTime\"? ?>([a-zA-Z 0-9,]*) </span>',html)
			mydate=re.sub('Updated on ','',match.group(1))
		else:
			match=re.search(r'<span id=\"?UpdateTime\"? ?>([a-zA-Z 0-9,]*) </span>',oldhtml)
			mydate=re.sub('Updated on ','',match.group(1))
	else:
		match=re.search(r'<span id=\"?UpdateTime\"? ?>([a-zA-Z 0-9,]*) </span>',html)
		mydate=re.sub('Updated on ','',match.group(1))
		with open(output, 'w') as f:
				f.write(html)
		print('rebuilt and wrote '+output)
	pagedict={}
	pagedict['name']=output.replace('../','')
	pagedict['date']=mydate
	PageList.append(pagedict.copy())
	return html

def check_for_new_former_students(news_dict,normal_dict):
	myRegex=re.compile('people/([A-Za-z-]+)\.html')
	for item in news_dict['News']:
		if 'processed' in item:
			if item['processed'].upper() == "YES":
				match=re.findall(myRegex,item['Text'])
				for tag in match:
					for student in normal_dict['Students']:
						if 'former' in student:
							if 'tag' in student:
								mytag=student['tag'];
							else: 
								mytag=student['FirstName']+student['LastName'];
							if tag == mytag:
								print('Made ' + tag + ' into a former student')
								wipe_news_item(item)
	return news_dict
	
def clear_automated_values_in_news_dict(news_dict):
	for item in news_dict['News']:
		wipe_news_item(item)
	return news_dict

def wipe_news_item(item):
	item.pop("processed", None)
	item.pop("name", None)
	item.pop("glyph", None)
	item['Text']=re.sub('(?:<a href=\\\"[A-Za-z]*GroupMembers.html#[A-Za-z-]*\\\"> *)+([A-Za-z,!\\\"\'. -]*)(?:</a>)+','\\1',item['Text']); #used to remove old hyperlinks
	item['Text']=re.sub('(?:<a href=\\\"people/[A-Za-z-]*.html\\\"> *)+([A-Za-z,!\\\"\'. -]*)(?:</a>)+','\\1',item['Text']); #used to remove old hyperlinks
	item['Text']=re.sub('(?:<a href=\\\"[A-Za-z-]*.html\\\"> *)+([A-Za-z,!\\\"\'. -]*)(?:</a>)+','\\1',item['Text']); #used to remove old hyperlinks
	return item
	
def process_dictionary(dict):
	ResearchAreaList = ''
	for area in dict['areas']:
		ResearchAreaList = ResearchAreaList + area['title']
	dict['ResearchAreaList']=ResearchAreaList
	return dict
		
def process_people_dictionary(people_dict, normal_dict):

	if not 'img' in people_dict['PI']:
		default_name='../graphics/people/'+people_dict['PI']['FirstName']+people_dict['PI']['LastName']+'.jpg'
		if not os.path.isfile(default_name):
			people_dict['PI']['img']='phoenixblack.png'
			people_dict['PI']['missingphoto']='Yes'
			print('Photo not found: '+default_name )
		else:
			glyph_name='../graphics/people/glyphs/'+people_dict['PI']['FirstName']+people_dict['PI']['LastName']+'.jpg'
			if (not os.path.isfile(glyph_name)) or (os.path.getmtime(glyph_name)<os.path.getmtime(default_name)):
				with open(default_name, 'r+b') as f:
					with Image.open(f) as image:
							glyph = resizeimage.resize_cover(image, [62, 64])
							glyph.save(glyph_name, image.format)
				print('Glyph Created: '+glyph_name )
	if not 'img' in people_dict['Admin']:
		default_name='../graphics/people/'+people_dict['Admin']['FirstName']+people_dict['Admin']['LastName']+'.jpg'
		if not os.path.isfile(default_name):
			people_dict['Admin']['img']='phoenixblack.png'
			people_dict['Admin']['missingphoto']='Yes'
			print('Photo not found: '+default_name )
		else:
			glyph_name='../graphics/people/glyphs/'+people_dict['Admin']['FirstName']+people_dict['Admin']['LastName']+'.jpg'
			if (not os.path.isfile(glyph_name)) or (os.path.getmtime(glyph_name)<os.path.getmtime(default_name)):
				with open(default_name, 'r+b') as f:
					with Image.open(f) as image:
							glyph = resizeimage.resize_cover(image, [62, 64])
							glyph.save(glyph_name, image.format)
				print('Glyph Created: '+glyph_name )
	for student in people_dict['Students']:
		if not 'img' in student:
			default_name='../graphics/people/'+student['FirstName']+student['LastName']+'.jpg'
			glyph_name='../graphics/people/glyphs/'+student['FirstName']+student['LastName']+'.jpg'
		else:
			default_name='../graphics/people/'+student['img']
			glyph_name='../graphics/people/glyphs/'+student['img']
		if not os.path.isfile(default_name):
			student['img']='phoenixblack.png'
			student['missingphoto']='Yes'
			print('Photo not found: '+default_name )
		else:
			if (not os.path.isfile(glyph_name)) or (os.path.getmtime(glyph_name)<os.path.getmtime(default_name)):
				with open(default_name, 'r+b') as f:
					with Image.open(f) as image:
							glyph = resizeimage.resize_cover(image, [62, 64])
							glyph.save(glyph_name, image.format)
				print('Glyph Created: '+glyph_name )
	
	for student in people_dict['Students']:
		if 'degrees' in student:
			student['degrees']=OrderDegrees(student['degrees'])
	return people_dict

def OrderDegrees(degrees):
	newlist=[None]*100
	iter=1
	for d in degrees:
		n=7
		if 'S.B' in d.upper(): n=3
		if 'SB' in d.upper(): n=3
		if 'B.S' in d.upper(): n=3
		if 'BS' in d.upper(): n=3
		if 'B.A' in d.upper(): n=4
		if 'BA' in d.upper(): n=4
		if 'A.B' in d.upper(): n=5
		if 'AB' in d.upper(): n=5
		if 'S.M' in d.upper(): n=2
		if 'SM' in d.upper(): n=2
		if 'M.S' in d.upper(): n=2
		if 'MS' in d.upper(): n=2
		if 'M.A' in d.upper(): n=3
		if 'MA' in d.upper(): n=3
		if 'A.M' in d.upper(): n=3
		if 'AM' in d.upper(): n=3
		if 'PH.D' in d.upper(): n=1
		if 'PHD' in d.upper(): n=1 
		if 'FELLOW' in d.upper(): n=0
		if 'POSTDOC' in d.upper(): n=0 
		#if n==7: print("Unable to sort degree: "+d)
		newlist[n*10+iter]=d
		iter=iter+1
	newlist=[x for x in newlist if x != None]
	return newlist
	
def process_peoplepages_dictionary(people_dict, normal_dict):
	for student in normal_dict['Students']:
		if not 'former' in student:
			for page in people_dict['PeoplePages']:
					if student['FirstName'] == page['FirstName'] and student['LastName'] == page['LastName']:
						if 'bio' in page:
							student['bio']=page['bio']
						if 'research' in page:
							student['research']=page['research']
						if 'accolades' in page:
							student['accolades']=page['accolades']
			student['about']="Yes"
			if not 'url' in student:
				student['url']=student['FirstName']+student['LastName']+'.html'
			for pub in normal_dict['pubs']:
				if 'PublicationName' in student:
					if student['PublicationName'] in pub['auth']:
						if not 'mypubs' in student:
							student['mypubs']=[]
						student['mypubs'].append(pub)
				else:
					if (student['LastName']+',' in pub['auth']) or (student['LastName']+' and' in pub['auth']) or (student['LastName']+'*' in pub['auth']):
						if not 'mypubs' in student:
							student['mypubs']=[]
						student['mypubs'].append(pub)
			

	for page in people_dict['PeoplePages']:
			if normal_dict['PI']['FirstName'] == page['FirstName'] and normal_dict['PI']['LastName'] == page['LastName']:
				if 'bio' in page:
					normal_dict['PI']['bio']=page['bio']
				if 'research' in page:
					normal_dict['PI']['research']=page['research']
				if 'accolades' in page:
					normal_dict['PI']['accolades']=page['accolades']
	normal_dict['PI']['about']="Yes"
	if not 'url' in normal_dict['PI']:
		normal_dict['PI']['url']=normal_dict['PI']['FirstName']+normal_dict['PI']['LastName']+'.html'
	count = 0	
	for pub in normal_dict['pubs']:
		if normal_dict['PI']['LastName'] in pub['auth']:
			if count < 10:
				if not 'mypubs' in normal_dict['PI']:
					normal_dict['PI']['mypubs']=[]
				normal_dict['PI']['mypubs'].append(pub)
				count +=1

	return normal_dict	
	
def process_news_dictionary(news_dict, normal_dict, output,title_dict,RebuildNews):
	# next line clears automated values in news_dict
	if RebuildNews==1:
		news_dict=clear_automated_values_in_news_dict(news_dict)
	news_dict=check_for_new_former_students(news_dict,normal_dict)
	for item in news_dict['News']:
		if 'processed' in item:
			if item['processed'].upper() == "NO":
				item.pop("processed", None)
				item.pop("name", None)
				item.pop("glyph", None)
		if not 'processed' in item:
			newtext=item['Text']
			item['glyph']=[];
			for student in normal_dict['Students']:
				if student['FirstName']+' '+student['LastName'] in item['Text']: 
					match=re.search(student['FirstName']+' '+student['LastName'],item['Text'])
					pos=match.start()
					if 'tag' in student:
						mytag=student['tag'];
					else: 
						mytag=student['FirstName']+student['LastName'];
					if 'url' in student:
						url = 'people/'+student['url']
					else:
						if 'former' in student:
							url="FormerGroupMembers.html#"+mytag
						else: 
							url="GroupMembers.html#"+mytag
					if 'img' in student:
						img="graphics/people/glyphs/"+student['img'];
					else:
						img="graphics/people/glyphs/"+student['FirstName']+student['LastName']+".jpg";
					alt=student['FirstName']+' '+student['LastName']
					item['glyph'].append({'url':url, 'img':img, 'alt':alt, 'position':pos})
					if 'missingphoto' in student:
						item['missingphoto']='Yes'
					newtext=newtext.replace(student['FirstName']+' '+student['LastName'],"<a href=\""+url+"\">"+student['FirstName']+" "+student['LastName']+"</a>")	
					newtext=re.sub("( *<a href=\""+url+"\">)+"," <a href=\""+url+"\">",newtext)	
					newtext=re.sub("(</a>)+","</a>",newtext)	
				elif 'Nickname' in student:
					if student['Nickname'] in item['Text']: 
						match=re.search(student['Nickname'],item['Text'])
						pos=match.start()
						if 'tag' in student:
							mytag=student['tag'];
						else: 
							mytag=student['FirstName']+student['LastName'];
						if 'url' in student:
							url = 'people/'+student['url']
						else:
							if 'former' in student:
								url="FormerGroupMembers.html#"+mytag
							else: 
								url="GroupMembers.html#"+mytag
						if 'img' in student:
							img="graphics/people/glyphs/"+student['img'];
						else:
							img="graphics/people/glyphs/"+student['FirstName']+student['LastName']+".jpg";
						alt=student['FirstName']+' '+student['LastName']
						item['glyph'].append({'url':url, 'img':img, 'alt':alt, 'position':pos})
						if 'missingphoto' in student:
							item['missingphoto']='Yes'
						newtext=newtext.replace(student['Nickname'],"<a href=\""+url+"\"> "+student['Nickname']+"</a>")	
						newtext=newtext.replace("<a href=\""+url+"\"> <a href=\""+url+"\">","<a href=\""+url+"\">")	
						newtext=newtext.replace("</a></a>","</a>")	
			PI=normal_dict['PI']
			if PI['LastName'] in item['Text']:
				match=re.search(PI['LastName'],item['Text'])
				pos=match.start()
				if 'url' in PI:
					url="people/"+PI['url']
				else:
					url="GroupMembers.html#"+PI['FirstName']+PI['LastName']
				if 'img' in PI:
					img="graphics/people/glyphs/"+PI['img'];
				else:
					img="graphics/people/glyphs/"+PI['FirstName']+PI['LastName']+".jpg";
				alt=PI['FirstName']+' '+PI['LastName']
				item['glyph'].append({'url':url, 'img':img, 'alt':alt, 'position':pos})
				newtext=newtext.replace(PI['FirstName']+' '+PI['LastName'],"<a href=\""+url+"\">"+PI['FirstName']+' '+PI['LastName']+"</a>")	
				newtext=newtext.replace('Prof. '+PI['LastName'],"<a href=\""+url+"\">"+PI['FirstName']+' '+PI['LastName']+"</a>")	
				newtext=re.sub("( *<a href=\""+url+"\">)+"," <a href=\""+url+"\">",newtext)	
				newtext=re.sub("(</a>)+","</a>",newtext)	
			Admin=normal_dict['Admin']
			if Admin['FirstName']+' '+Admin['LastName'] in item['Text']:
				match=re.search(Admin['LastName'],item['Text'])
				pos=match.start()
				if 'url' in Admin:
					url = 'people/'+Admin['url']
				else:
					url="GroupMembers.html#"+Admin['FirstName']+Admin['LastName']
				if 'img' in Admin:
					img="graphics/people/glyphs/"+Admin['img'];
				else:
					img="graphics/people/glyphs/"+Admin['FirstName']+Admin['LastName']+".jpg";
				alt=Admin['FirstName']+' '+Admin['LastName']
				item['glyph'].append({'url':url, 'img':img, 'alt':alt, 'position':pos})
				if Admin['FirstName']+' '+Admin['LastName'] in item['Text']: 
					newtext=newtext.replace(Admin['FirstName']+' '+Admin['LastName'],"<a href=\""+url+"\">"+Admin['FirstName']+' '+Admin['LastName']+"</a>")	
				else:
					newtext=newtext.replace(Admin['LastName'],"<a href=\""+url+"\">"+Admin['LastName']+"</a>")	
				newtext=re.sub("( *<a href=\""+url+"\">)+"," <a href=\""+url+"\">",newtext)	
				newtext=re.sub("(</a>)+","</a>",newtext)	

			if not 'name' in item:
				myname=''
				for title in title_dict['titles']:
					if not isinstance(title['key'], list):
						if title['key'].lower() in item['Text'].lower():
							myname=title['label'];
					else: 
						foundit=1
						for mykey in title['key']:
							if not mykey.lower() in item['Text'].lower():
								foundit=0
						if foundit==1:
							myname=title['label'];
				if myname != '':
					item['name']=myname;	
				else:
					print ("Need title for \n \t"+item['Text'])
					item['missingtitle']='Yes'
			item['Text']=newtext
			item['glyph']=sorted(item['glyph'], key=operator.itemgetter('position'))
			for myglyph in item['glyph']:
				myglyph.pop("position", None)
			if len(item['glyph'])==0:
				item['glyph'].append({'url':'index.html', 'img':'graphics/people/glyphs/SimonLab.png', 'alt':'SimonLab'})
			item['processed']='Yes'
			if 'missingphoto' in item:
				item['processed']='No'
				item.pop("missingphoto",None)
			if 'missingtitle' in item:
				item['processed']='No'
				item.pop("missingphoto",None)
			
	if not 'Comment' in news_dict:
		news_dict['Comment']={"Date": "","Text": ""}
	
	myjson=json.dumps(news_dict, sort_keys=True,separators=(',', ': '));
	myjson=re.sub('\{\"Comment\": \{\"Date\": \"\",\"Text\": \"\"\},\"News\": \[','{\"Comment\": \n\t\t{\"Date\": \"\",\"Text\": \"\"},\n\"News\": [\n\t\t',myjson);
	myjson=re.sub('\{\"News\": \[','{\"News\": [\n\t\t',myjson);
	myjson=re.sub('},{"Date":','},\n\t\t{"Date":',myjson);
	
	if not RebuildNews:
		try:
			with open(output, 'r') as f:
				oldjson = f.read();
		except (OSError, IOError) as e:
			oldjson='xxxx'
		if myjson != oldjson:
			with open(output, 'w') as f:
				f.write(myjson)
			print('wrote '+output)
	else:
		with open(output, 'w') as f:
			f.write(myjson)
		print('wrote '+output)
	news_dict['News']=sorted(news_dict['News'], key=lambda x: datetime.datetime.strptime(x['Date'], '%m/%d/%Y'),reverse=True)
	return news_dict


#Begin Main Program
	
RebuildAll = 1
RebuildNews = 1
sys.argv = [x.strip(' ') for x in sys.argv]
try:
	 opts, args = getopt.getopt(sys.argv[1:],"rhn",["rebuild_all","help","rebuild_news"])
except getopt.GetoptError as err:
	print(err)
	sys.exit(2)
for opt in opts:
	if opt[0] in ('-h','--help'):
		print('build-site.py [-r | --rebuild_all] [-n | -- rebuild_news] [-h | --help] ')
		sys.exit(2)
	else:
		if opt[0].strip() in ("-r", "--rebuild_all"):
			RebuildAll = 1
			print('rebuilding all...')
		if opt[0].strip() in ("-n", "--rebuild_news"):
			RebuildNews = 1
			print('rebuilding news...')
			
cfg = json.load(open('index.json', 'r'))
cfg =  process_dictionary( cfg)
cfg_pub = json.load(open('publications.json', 'r'))
cfg.update(cfg_pub)
cfg_people = json.load(open('people.json', 'r'))
cfg_people = process_people_dictionary(cfg_people, cfg)
cfg.update(cfg_people)
cfg_peoplepages = json.load(open('peoplepages.json', 'r'))
cfg = process_peoplepages_dictionary(cfg_peoplepages, cfg)
cfg_news_titles = json.load(open('news_titles.json', 'r'))
cfg_news = json.load(open('news.json', 'r'))
cfg_news = process_news_dictionary(cfg_news, cfg, 'news.json',cfg_news_titles,RebuildNews)
cfg.update(cfg_news)
cfg['updateTime']=datetime.date.today().strftime('Updated on %B %d, %Y').replace(' 0',' ')

PageList=[]


render_template_to_output(name='index.html', vars=cfg, output='../index.html',rebuild=RebuildAll)
render_template_to_output(name='publications.html', vars=cfg, output='../publications.html',rebuild=RebuildAll)
render_template_to_output(name='research.html', vars=cfg, output='../research.html',rebuild=RebuildAll)
render_template_to_output(name='contact.html', vars=cfg, output='../contact.html',rebuild=RebuildAll)
render_template_to_output(name='GroupMembers.html', vars=cfg, output='../GroupMembers.html',rebuild=RebuildAll)
# render_template_to_output(name='FormerGroupMembers.html', vars=cfg, output='../FormerGroupMembers.html',rebuild=RebuildAll)
render_template_to_output(name='news.html', vars=cfg, output='../news.html',rebuild=RebuildAll)
# render_template_to_output(name='meetings.html', vars=cfg, output='../meetings.html',rebuild=RebuildAll)
# render_template_to_output(name='pictures.html', vars=cfg, output='../pictures.html',rebuild=RebuildAll)
# render_template_to_output(name='FPGA.html', vars=cfg, output='../FPGA.html',rebuild=RebuildAll)
# render_template_to_output(name='Movies.html', vars=cfg, output='../Movies.html',rebuild=RebuildAll)
#render_template_to_output(name='faq.html', vars=cfg, output='../faq.html',rebuild=RebuildAll)
#render_template_to_output(name='laboratories.html', vars=cfg, output='../laboratories.html',rebuild=RebuildAll)
#render_template_to_output(name='sensatronics.html', vars=cfg, output='../sensatronics.html',rebuild=RebuildAll)
render_template_to_output(name='applynow.html', vars=cfg, output='../applynow.html',rebuild=RebuildAll)
# render_template_to_output(name='404.html', vars=cfg, output='../404.html',rebuild=RebuildAll)
# render_template_to_output(name='funding.html', vars=cfg, output='../funding.html',rebuild=RebuildAll)
# render_template_to_output(name='links.html', vars=cfg, output='../links.html',rebuild=RebuildAll)
minify_css_to_output(name='../css/bootstrap.css',  output='../css/bootstrap.min.css',rebuild=RebuildAll)
minify_css_to_output(name='../css/simonlab.css',  output='../css/simonlab.min.css',rebuild=RebuildAll)
minify_css_to_output(name='../font-awesome/css/font-awesome.css',  output='../font-awesome/css/font-awesome.min.css',rebuild=RebuildAll)

cfg['DirectoryPrefix']='../';
for area in cfg['areas']:
		cfg['myarea']=area;
		render_template_to_output(name='area.html', vars=cfg, output='../research/'+area['url'],rebuild=RebuildAll)

#for lab in cfg['laboratories']['labs']:
#		cfg['mylab']=lab;
#		render_template_to_output(name='lab.html', vars=cfg, output='../labs/'+lab['url'],rebuild=RebuildAll)

for student in cfg['Students']:
		if "about" in student:
			cfg['me']=student
			render_template_to_output(name='peoplepage.html', vars=cfg, output='../people/'+student['url'],rebuild=RebuildAll)
if "about" in cfg['PI']:
	cfg['me']=cfg['PI']
	render_template_to_output(name='peoplepage.html', vars=cfg, output='../people/'+cfg['PI']['url'],rebuild=RebuildAll)


GenerateSiteMap(list=PageList,output='../sitemap.xml',rebuild=RebuildAll)

import os
#os.system("""rsync -avz "/Users/jon/Dropbox/Faculty Stuff/Simonlab Website Materials/NewWebsite_D1/" root@simonlab-server.uchicago.edu:/usr/local/www/simonlab/ """)
