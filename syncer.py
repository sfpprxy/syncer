import requests
from bs4 import BeautifulSoup
import os
import time

# temp dev variables

# module info

# hints
downloading = 'Start downloading files in 3 seconds...It may take few minutes, depends on your network. ' \
              'You can minimize this window while downloading'

# Authorization
username = 'cuiq4'
password = 'Cucu.109'
login_action = 'https://cumoodle.coventry.ac.uk/login/index.php'
user = {'username': username, 'password': password}
my_course = 'https://cumoodle.coventry.ac.uk/my/index.php'
s = requests.session()
s.post(login_action, data=user)


def parser(url):
    source = s.get(url)
    return BeautifulSoup(source.text, "html.parser")


def get_modules_list(url):
    name_list = []
    link_list = []
    soup = parser(url)
    i = 1
    # locate module table
    for module in soup.find(id='current').find_all('a'):
        name = module.string
        link = module.get('href')
        print(i, name)
        i += 1
        name_list.append(name)
        link_list.append(link)
    return name_list, link_list


def get_module_resource():
    # choice module
    get = get_modules_list(my_course)
    choice = int(input(' \n Choice module number(then hit ENTER): ')) - 1
    # TODO: try expect naughty input, e.g. ENTER
    module_name = get[0][choice]
    module_link = get[1][choice]

    # download module page
    downloader(module_link, True)

    # preparation: locate content of this module
    soup = parser(module_link)
    # TODO: extract a mini function add to parser()
    ul = soup.find_all('ul', {'class': 'topics'})
    ul = BeautifulSoup(str(ul), "html.parser")
    contents = ul.find_all('div', {'class': 'content'})
    contents = BeautifulSoup(str(contents), "html.parser")

    # '''Notice: Beautiful.content.number > moodle_html.content.number'''
    resource = []
    for content in contents:
        content = BeautifulSoup(str(content), "html.parser")
        this_topic = []

        # get topic_name
        tmp = content.find_all('h3', {'class': 'sectionname'})  # KEY_INFO
        for topic_name in tmp:
            topic_name = topic_name.string
            this_topic.append(topic_name)

        # preparation: get section of each topic
        tmp = content.find_all('ul', {'class': 'section img-text'})
        tmp = BeautifulSoup(str(tmp), "html.parser")

        files = tmp.find_all('a', {'class onclick': ''})  # KEY_INFO
        for file in files:
            # get file_urls
            url = file.get('href') + '&redirect=1'
            if '/mod/resource/' in url:  # KEY_INFO
                this_topic.append(url)

            # get file_names
            if '/mod/resource/' in url:  # KEY_INFO
                file = BeautifulSoup(str(file), "html.parser")

                sp = file.find_all('span', {'class': 'instancename'})  # KEY_INFO
                sp = str(sp)
                start = '<span class="instancename">'
                end = '<span'
                start = sp.find(start) + len(start)
                end = sp.find(end, start)
                pure_name = sp[start:end]

                def check(link):
                    acceptable = ['pdf', 'pdf', 'document', 'docx', 'powerpoint', 'pptx',
                                  'spreadsheet', 'xlsx', 'archive', 'zip']
                    last = link.split('/')[-1]
                    for ac in acceptable:
                        if ac in last:
                            return acceptable[acceptable.index(ac) + 1]
                    return 'Not acceptable file type'

                img = file.find('img', {'': ''})  # KEY_INFO
                t = img.get('src')
                extension = check(t)

                name = pure_name + '.' + extension
                this_topic.append(name)

    # generate one list of this module's content
        if len(this_topic) != 0:
            resource.append(this_topic)
    print(resource)
    return module_name, resource


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


def old_assembler(urls):
    dead_link = 0
    for url in urls:
        try:
            downloader(url)
        # handle unreachable url
        except requests.RequestException:
            dead_link += 1
            print(str(dead_link) + ' UNREACHABLE FILE\n' + urls + '\n')
            continue


# TODO: two-layer loops: inside iterate each file in[[]], outside iterate each topic in[]
def assembler():
    data = get_module_resource()

    # create module folder
    module_name = data[0]
    if not os.path.exists(module_name):
        os.makedirs(module_name)
    # else:
    #   TODO: download files into existing module_folder

    resource = data[1]
    for i in resource:
        sub_list = resource[resource.index(i)]

        # create topic folder
        folder_name = sub_list[0]
        print(folder_name)
        dist = os.path.join(module_name, folder_name)
        os.makedirs(dist)

        # download files into folder
        for file in sub_list[1:]:
            if sub_list[1:].index(file) % 2 == 0:
                file_url = file
                print(file_url)
            else:
                file_name = file
                print(file_name)
        # TODO: download file











# uuu = 'https://cumoodle.coventry.ac.uk/mod/resource/view.php?id=891409&redirect=1'
# u = s.get(uuu)
# print(u.url)

assembler()
