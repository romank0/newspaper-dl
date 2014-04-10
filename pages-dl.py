
import urllib2, urllib
import json
import subprocess
import re
import sys

if len(sys.argv) != 3:
    print "usage: pages-dl start_page_url cookie"
    sys.exit(1)


start_page_url = sys.argv[1]
cookie = sys.argv[2]

#start_page_url = 'http://fakty-i-komentarii.journals.ua/reader/8520.html'
#cookie = 'jv_site_enter_time_108801=1396864511564; jv_close_time_108801=1396875899696; jv_agent_info_108801=134389; SSN=0n1c6qynhgys0s04wsg44488wwwgk4gcefb66l48b5; TMR=11+Apr+2014+08%3A48%3A40+UTC; CAUTH=25449%5D%5BeJzbc95q6RP%2F6e0qLRN%2FBc7lM%2BJg2%2FIGAG%2BfCcs%3D%5D%5Bn3u28s; _ga=GA1.2.1679747763.1396864509; jv_pages_count_108801=17; CNAME=viraxyz; CCASH=0.00'

START_PAGE_PARAM = re.compile('currentPageId: "(.*)"')

"""
This is extract from main page
iipServerBaseUrl: "http://jreader.digitaljournals.com.ua/iipsrv/iipsrv.fcgi?FIF=/store1/8520/pages/",
backendServer: "http://fakty-i-komentarii.journals.ua/reader/service?",
currentPageId: "60wj9u0hevswccc8sgcgw0gk00010000_8520",
"""

THUMBS_URL='http://fakty-i-komentarii.journals.ua/reader/thumb' 
PAGE_INFO_URL = 'http://fakty-i-komentarii.journals.ua/reader/service?&z=5&p={page_num}d&id={page_id}'
PAGE_IMAGE_URL = 'http://jreader.digitaljournals.com.ua/iipsrv/iipsrv.fcgi?FIF=/store1/{magazine_id}/pages/{page_id}.tif'

def execute(req):
    req.add_header('Cookie', cookie)
    return urllib2.urlopen(req).read()


def post(url, data):
    page_data = urllib.urlencode(data)
    req = urllib2.Request(url, page_data)
    return execute(req)

def get(url):
    req = urllib2.Request(url)
    return execute(req)

def parse_start_page(content):
    for line in content.split('\n'):
        match = START_PAGE_PARAM.match(line)
        if match:
            return match.group(1)

start_page_content = get(start_page_url)

start_page = parse_start_page(start_page_content)
print "start page: " + start_page

magazine_id = start_page.split('_')[1]

def download_page(page_num, c, r, url):
    print "downloading page #%d images=(%d,%d) from %s"%(page_num,c,r,url)
    subprocess.call(['bash', 'page-dl', str(c), str(r), url, "page_%d.jpg"%page_num])


def get_thumbs(page_id):
    print "getting pages..."
    content = post(THUMBS_URL, { 'uuid' : start_page })
    thumbs = json.loads(content)
    return thumbs['thumb']


def download_pages(thumbs):
    print "extracting pages..."
    page_num = 1
    for thumb in thumbs:
        page_id = thumb['thumb_path'].split('/')[-1].split('.')[0]
        print "page: " + page_id
        pages_info_json = get(PAGE_INFO_URL.format(page_num=page_num, page_id=page_id))
        pages_info = json.loads(pages_info_json) 
        page_info = pages_info['pgs'][0]
        c = page_info['c']
        r = page_info['r']
        url = PAGE_IMAGE_URL.format(magazine_id=magazine_id, page_id=page_id)
        download_page(page_num, c, r, url)
        page_num = page_num + 1

download_pages(get_thumbs(start_page))

