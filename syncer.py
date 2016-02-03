import requests
from bs4 import BeautifulSoup
import time

# temp dev variables

# module info

# hints
downloading = 'Start downloading...It may take few minutes, depends on your network.'

# Authorization
login_action = 'https://cumoodle.coventry.ac.uk/login/index.php'
user = {'username': 'cuiq4', 'password': 'Cucu.109'}
my_course = 'https://cumoodle.coventry.ac.uk/my/index.php'
s = requests.session()
s.post(login_action, data=user)


def parser(url):
    source = s.get(url)
    return BeautifulSoup(source.text, "html.parser")


def check_format(url):
    file_format = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.zip']
    last = url.split('/')[-1]
    for fm in file_format:
        if fm in last:
            # good to go
            return True


def downloader(url, is_module_page=False):
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
    # locate module table, TODO: try to change to matrix multiplication
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
    get = get_module_list(my_course)
    choice = int(input(' \n Choice module number(then hit ENTER): ')) - 1
    # TODO: try expect naughty input
    module_link = get[1][choice]

    # download module page
    # downloader(module_link, True)

    # preparation for getting topics & files
    soup = parser(module_link)
    ul = soup.find_all('ul', {'class': 'topics'})
    ul = BeautifulSoup(str(ul), "html.parser")
    content = ul.find_all('div', {'class': 'content'})
    content = BeautifulSoup(str(content), "html.parser")

    section_name = content.find_all('h3', {'class': 'sectionname'})
    print(section_name)

    section_img_text = content.find_all('ul', {'class': 'section img-text'})

    before_dd = BeautifulSoup(str(section_img_text), "html.parser")
    dd = before_dd.find_all('a', {'class onclick': ''})
    for hh in dd:
        print(hh.get('href'))



    #     topic_name = topic.string
    #     topic_list.append(topic_name)
    #     print(topic_list[-1])
    # topic_list.pop(0)  # remove hidden topic

    # print(topic_list)
    # print(len(topic_list))


get_module_info()
