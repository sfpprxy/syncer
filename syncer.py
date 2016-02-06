import requests
from bs4 import BeautifulSoup
import re
import time

# temp dev variables

# module info

# hints
downloading = 'Start downloading files in 3 seconds...It may take few minutes, depends on your network. ' \
              'You can minimize this window while downloading'

# Authorization
login_action = 'https://cumoodle.coventry.ac.uk/login/index.php'
user = {'username': 'cuiq4', 'password': 'Cucu.109'}
my_course = 'https://cumoodle.coventry.ac.uk/my/index.php'
s = requests.session()
s.post(login_action, data=user)


def parser(url):
    source = s.get(url)
    return BeautifulSoup(source.text, "html.parser")


# def check_format(url):
#     # file_format = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.zip']
#     file_format = ['.pdf', '.docx', '.pptx', '.xlsx', '.zip']
#     last = url.split('/')[-1]
#     for fm in file_format:
#         if fm in last:
#             # good to go
#             return True


def check_url(url):
    acceptable = ['pdf', 'pdf', 'document', 'docx', 'powerpoint', 'pptx', 'spreadsheet', 'xlsx', 'archive', 'zip']
    last = url.split('/')[-1]
    for ac in acceptable:
        if ac in last:
            # good to go
            return acceptable[acceptable.index(ac) + 1]
    return 'Not acceptable file type.'


def downloader(url, is_module_page=False):
    # TODO: try catch dead_url
    # from http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
    local_filename = url.split('/')[-1]
    r = s.get(url, stream=True)
    if is_module_page:
        local_filename = 'this module page.html'
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename


def assembler():
    dead_link = 0
    global urls
    for url in urls:
        try:
            downloader(url)
        # handle unreachable url
        except requests.RequestException:
            dead_link += 1
            print(str(dead_link) + ' UNREACHABLE FILE\n' + urls + '\n')
            continue


def get_module_list(url):
    name_list = []
    link_list = []
    soup = parser(url)
    # locate module table
    i = 1
    for module in soup.find(id='current').find_all('a'):
        name = module.string
        link = module.get('href')
        print(i, name)
        i += 1
        name_list.append(name)
        link_list.append(link)
    return name_list, link_list


def get_module_info():
    # choice module
    global pure_name, extension
    get = get_module_list(my_course)
    choice = int(input(' \n Choice module number(then hit ENTER): ')) - 1
    # TODO: try expect naughty input, e.g. ENTER
    module_link = get[1][choice]

    # download module page
    # downloader(module_link, True)

    # preparation: getting topics & files
    soup = parser(module_link)
    # TODO: extract a mini function add to parser()
    ul = soup.find_all('ul', {'class': 'topics'})
    ul = BeautifulSoup(str(ul), "html.parser")
    contents = ul.find_all('div', {'class': 'content'})
    contents = BeautifulSoup(str(contents), "html.parser")

    # '''Inconsistency: Beautiful.content.number > moodle_html.content.number !!'''
    for content in contents:
        content = BeautifulSoup(str(content), "html.parser")

        # get topic_name
        tmp = content.find_all('h3', {'class': 'sectionname'})  # KEY_INFO
        for topic_name in tmp:
            topic_name = topic_name.string
            if topic_name == 'General':  # hack
                continue
            print(topic_name)

        # preparation: get section of each topic
        tmp = content.find_all('ul', {'class': 'section img-text'})
        tmp = BeautifulSoup(str(tmp), "html.parser")

        resource = tmp.find_all('a', {'class onclick': ''})  # KEY_INFO
        for file in resource:
                # get file_url
                url = file.get('href') + '&redirect=1'
                if '/mod/resource/' in url:  # KEY_INFO
                    print(url)
                # get file_name
                if '/mod/resource/' in url:  # KEY_INFO
                    file = BeautifulSoup(str(file), "html.parser")

                    span = file.find_all('span', {'class': 'instancename'})  # KEY_INFO
                    for sp in span:
                        sp = str(sp)
                        start = '<span class="instancename">'
                        end = '<span'
                        start = sp.find(start) + len(start)
                        end = sp.find(end, start)
                        pure_name = sp[start:end]

                    img = file.find_all('img', {'': ''})  # KEY_INFO
                    for t in img:
                        t = t.get('src')
                        extension = check_url(t)

                    name = pure_name + '.' + extension
                    print(name)



        # print('\n')


# uuu = 'https://cumoodle.coventry.ac.uk/mod/resource/view.php?id=891409&redirect=1'
# u = s.get(uuu)
# print(u.url)

get_module_info()
