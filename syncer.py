import requests
from bs4 import BeautifulSoup
import os
import sys
import time
import traceback


def set_cwd():
    exe_path = os.path.realpath(os.path.dirname(sys.argv[0]))
    os.chdir(exe_path)


def welcome():
    print(INTRO + MAKE_CLEAR + LOGIN_HINT)


def login():
    def input_user_info():
        global USERNAME, PASSWORD
        USERNAME = input('\nEnter your Moodle username:')
        PASSWORD = input('Enter your Moodle password:')
        if USERNAME == '' or PASSWORD == '':
            print('They can not be empty, please try again.')
            input_user_info()

    def save_user_info():
        with open(PROFILE, 'w') as p:
            p.write(USERNAME + '\n' + PASSWORD)

    def read_user_info():
        global USERNAME, PASSWORD
        with open(PROFILE) as p:
            user = p.read().splitlines()
        USERNAME = user[0]
        PASSWORD = user[1]

    def authorization():
        user = {'username': USERNAME, 'password': PASSWORD}
        global s
        s = requests.session()
        return s.post(LOGIN_ACTION, data=user)

    if os.path.isfile(PROFILE):  # not first time use
        read_user_info()
    else:  # first time use
        input_user_info()

    # do not know if username and password is correct yet
    print('Connecting to Moodle...')

    if 'Log in to the site' in authorization().text:  # login fail
        print('\nWrong username or password, please try again.')
        input_user_info()
        save_user_info()
        login()
    else:  # username and password correct, login success
        print('\nLogin success!\n')
        save_user_info()


def parser(url):
    source = s.get(url)
    return BeautifulSoup(source.text, "html.parser")


def get_modules_list(url):
    name_list = []
    link_list = []
    soup = parser(url)
    i = 1
    print('', 0, ': ', 'Author Info')
    # locate module table
    for module in soup.find(id='current').find_all('a'):
        name = module.string
        link = module.get('href')
        print('', i, ': ', name)
        i += 1
        name_list.append(name)
        link_list.append(link)
    return name_list, link_list


def get_module_resource():
    def choice_module():
        get = get_modules_list(MY_COURSE)
        u = 0
        hit = 0
        for _ in range(16):
            def hint():
                nonlocal hit
                hit += 1
                i = hit
                if i == 1:
                    print(WHOOPS)
                if i == 2:
                    print(PLEASE)
                if 2 < i < 16:
                    print(DON)

            try:
                choice = int(input(ASK)) - 1
                if choice == -1:
                    u += 1
                    print(AUTHOR + SUGGEST)
                elif choice in range(len(get[0])):
                    module = get[0][choice]
                    link = get[1][choice]
                    input(CONFIRM)
                    return module, link
                else:
                    hint()
            except ValueError:
                hint()
            if hit + u == 15:
                print(EGG)
                time.sleep(3)
                exit()

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
            if topic_name[-1] == ' ':  # convert unacceptable topic_name for Windows
                topic_name = topic_name[:-1]
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


# Sync resources and organize them properly
def assembler():
    module = get_module_resource()

    # create module folder
    module_name = module[0]
    if not os.path.exists(module_name):
        os.makedirs(module_name)

    module_link = module[1]
    downloader(module_link, module_name, 'This module page.html')

    resource = module[2]
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
    finish()


def finish():
    where = os.getcwd()
    print('\nJob done!')
    print('\nYou can find a module folder in ' + where + ' and your password is saved in profile.')
    i = input("\nPress 'ENTER' to exit or press or Input 's' to sync another module:")
    if i == 's':
        assembler()


# WELCOME
AUTHOR = ('Joe Cui, study in Software Development. Email: cuiq4@uni.coventry.ac.uk'
          '\nYou can see the source code at https://github.com/sfpprxy/syncer')
INTRO = ('\nHi there, this is a simple tool that can automatically download/sync resources from Moodle '
         'and organize them in a clear way for you.\nIn a word, save you bunch of time!')
MAKE_CLEAR = '\n\nThis tool will NOT collect any of your personal information.'
SUGGEST = '\nIf you have any questions or suggestions, feel free to contact me :)\n'
LOGIN_HINT = '\n\nYou only need to login once, after that this tool will remember the password for you.'

# HINTS
ASK = '\nInput module number in list(then hit ENTER): '
WHOOPS = 'Whoops! It seems you input the wrong character.'
PLEASE = 'Please input numbers in range :)'
DON = "Don't be too curious ;)"
EGG = '\n...gnihsarc ggE\n): laem a uoy yub lliw I em tcatnoc ,gge retsaE eht dnif uoY !woW\n'[::-1]
CONFIRM = ("\nDownloading files will take a minute, depends on your network. "
           "\n\nPress 'ENTER' again to confirm")

# AUTHORIZATION
PROFILE = 'profile'
USERNAME = ''
PASSWORD = ''
MY_COURSE = 'https://cumoodle.coventry.ac.uk/my/index.php'
LOGIN_ACTION = 'https://cumoodle.coventry.ac.uk/login/index.php'


# noinspection PyBroadException
def main():
    try:
        set_cwd()
        welcome()
        login()
        assembler()
    except:
        tb = traceback.format_exc()
        with open('dump', 'w') as p:
            p.write(tb)
        print(tb)
        print(AUTHOR)
        input('Unknow error occured. Please contact author, thank you!')
    finally:
        pass


# Initiate program
main()
