import requests
import urllib.request
from bs4 import BeautifulSoup
import time

# temp dev variables
file_url = 'https://cumoodle.coventry.ac.uk/pluginfile.php/1159129/mod_resource/content/1/M19COM/Worksheets/m19com_lab2_Code_Person_class.zip'
urls = ['https://ck/ple.php', 'freak_out',
        'https://cumoodle.coventry.ac.uk/pluginfile.php/1159129/mod_resource/content/1/M19COM/Worksheets/m19com_lab2_Code_Person_class.zip',
        '66']

# Authorization
login_action = 'https://cumoodle.coventry.ac.uk/login/index.php'
user = {'username': 'cuiq4', 'password': 'Cucu.109'}
my_course = 'https://cumoodle.coventry.ac.uk/my/index.php'
s = requests.session()
s.post(login_action, data=user)


def downloader(url):
    # http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
    local_filename = url.split('/')[-1]
    r = s.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename


def assembler():
    dead_link = 0
    global urls
    for urls in urls:
        try:
            downloader(urls)
        # handle unreachable url
        except requests.exceptions.RequestException:
            dead_link += 1
            print(str(dead_link) + ' UNREACHABLE FILE\n' + urls + '\n')
            continue


def get_module_info(url):
    source = s.get(url)
    soup = BeautifulSoup(source.text, "html.parser")
    # locate module table, TODO: change to matrix multiplication
    name_list = []
    link_list = []
    i = 1
    for module in soup.find(id='current').find_all('a'):
        name = module.string
        link = module.get('href')
        print(i, name)
        i += 1
        name_list.append(name)
        link_list.append(link)
    # print(name_list)
    # print(link_list)


def enter_module():
    get_module_info(my_course)
    choice = input()
    print(choice)

# for topic in soup.findAll('h3', {'class', 'sectionname'}):
#     topic_name = topic.string
#     print(topic_name)

get_module_info(my_course)
