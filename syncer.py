import requests
from bs4 import BeautifulSoup
import os


def parser(url):
    source = s.get(url)
    return BeautifulSoup(source.text, "html.parser")


def get_modules_list(url):
    name_list = []
    link_list = []
    soup = parser(url)
    i = 1
    print(0, '  ', 'Contact author')
    # locate module table
    for module in soup.find(id='current').find_all('a'):
        name = module.string
        link = module.get('href')
        print(i, '  ', name)
        i += 1
        name_list.append(name)
        link_list.append(link)
    return name_list, link_list


def get_module_resource():
    def choice_module():
        get = get_modules_list(my_course)
        u = 0
        hit = 0
        for _ in range(16):
            def hint():
                nonlocal hit
                hit += 1
                i = hit
                if i == 1:
                    print(whoops)
                if i == 2:
                    print(please)
                if 2 < i < 16:
                    print(don)
            try:
                choice = int(input(ask)) - 1
                if choice == -1:
                    u += 1
                    print(author)
                elif choice in range(len(get[0])):
                    module = get[0][choice]
                    link = get[1][choice]
                    input(confirm)
                    return module, link
                else:
                    hint()
            except ValueError:
                    hint()
            if hit + u == 16:
                print(egg)

    # preparation: locate content of this module
    a = choice_module()
    module_name = a[0]
    module_link = a[1]
    soup = parser(module_link)
    # TODO later: extract a mini function add to parser()
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
                end = '<'
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
                    return 'Unknown file type'

                img = file.find('img', {'': ''})  # KEY_INFO
                try:
                    t = img.get('src')
                    extension = check(t)
                    name = pure_name + '.' + extension
                    this_topic.append(name)
                except AttributeError:
                    extension = 'Unknown file'
                    name = 'Hidden file on Moodle' + '.' + extension
                    this_topic.append(name)

    # generate ONE list of this module's content
        if len(this_topic) != 0:
            resource.append(this_topic)
    return module_name, module_link, resource


def downloader(url, path, file_name):
    # TODO later: try catch dead_url
    # from http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
    r = s.get(url, stream=True)
    with open(os.path.join(path, file_name), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return file_name


def assembler():
    data = get_module_resource()

    # create module folder
    module_name = data[0]
    if not os.path.exists(module_name):
        os.makedirs(module_name)

    downloader(data[1], module_name, 'This module page.html')

    resource = data[2]
    for i in resource:
        sub_list = resource[resource.index(i)]

        def convert_error_name(name):
            error = ['/', '|', '"', ':', '?', '*', '<', '>']
            for x in error:
                if x in name:
                    name = name.replace(x, '')
            return name

        # create topic folder
        folder_name = sub_list[0]
        folder_name = convert_error_name(folder_name)
        dist = os.path.join(module_name, folder_name)
        if not os.path.exists(dist):
            os.makedirs(dist)

        # download files into folder
        for file in sub_list[1:]:
            index = sub_list[1:].index(file)
            if index % 2 == 0:
                file_url = file

                file_name = sub_list[index + 2]
                file_name = convert_error_name(file_name)

                file_path = os.path.join(dist)

                # sync
                if not os.path.isfile(os.path.join(file_path, file_name)):
                    print('downloading....', file_name)
                    downloader(file_url, file_path, file_name)
                else:
                    print('file existed...', file_name)

# Welcome
author = 'Joe Cui, study in Software Engineering. Email: cuiq4@uni.coventry.ac.uk'

# hints
ask = '\nChoice module number(then hit ENTER): '
whoops = 'Whoops! It seems you input the wrong character.'
please = 'Please input numbers in range :)'
don = "Don't be too curious ;)"
egg = '\n...gnihsarc ggE\n): laem a uoy yub lliw I em tcatnoc ,gge retsaE eht dnif uoY !woW\n'[::-1]
confirm = '\nDownloading files will take a minute, depends on your network. ' \
          'You can minimize this window while syncing. \n\nPress ENTER again to start: '

# Authorization
# TODO: custom login, save user
username = 'cuiq4'
password = 'Cucu.109'
login_action = 'https://cumoodle.coventry.ac.uk/login/index.php'
user = {'username': username, 'password': password}
my_course = 'https://cumoodle.coventry.ac.uk/my/index.php'
s = requests.session()
s.post(login_action, data=user)

assembler()

