import sys
import os
from bs4 import BeautifulSoup
import cssutils
import mimetypes
import base64
import requests
from urlparse import urljoin

FILE_PARAM = '-f'
NAME_PARAM = '-n'
CSS_SEPARATOR = '$$'
TAGS = ['link', 'script', 'img']
PROTOCOLS = ['http://', 'https://']

mimetypes.init()
mimetypes.knownfiles

external = False

def main():
    global external

    validate()

    index = sys.argv.index(FILE_PARAM) + 1
    name_index = sys.argv.index(NAME_PARAM) + 1

    if any(p in sys.argv[index] for p in PROTOCOLS):
        external = True

    if external:
        response = requests.get(sys.argv[index])
        if response.status_code != 200:
            sys.exit('Error while trying to retrieve external resource: ' + sys.argv[index])
        html = BeautifulSoup(response.text, 'html5lib')
    else:
        html = BeautifulSoup(open(sys.argv[index]).read(), 'html5lib')

    tags = sum([html.find_all(tag) for tag in TAGS], [])

    for tag in tags:

        if external:
            if 'href' in tag.attrs and 'rel' in tag.attrs and tag['rel'] == 'stylesheet':
                path = urljoin(sys.argv[index], tag.get('href'))
            elif 'src' in tag.attrs:
                path = urljoin(sys.argv[index], tag.get('src'))
            else:
                continue
        else:
            if 'href' in tag.attrs:
                path = os.path.join(os.path.dirname(sys.argv[index]), tag.get('href'))
            elif 'src' in tag.attrs:
                path = os.path.join(os.path.dirname(sys.argv[index]), tag.get('src'))
            else:
                continue

        if any(p in path for p in PROTOCOLS):
            if tag.name == 'script':
                response = requests.get(path)
                if response.status_code != 200:
                    sys.exit('Error while trying to retrieve external resource: ' + path)
                content = response.text
            elif tag.name == 'img':
                response = requests.get(path.replace('\\', '/'), stream=True)
                if response.status_code != 200:
                    sys.exit('Error while trying to retrieve external resource: ' + path + ' Response code: ' + str(response.status_code))

                response.raw.decode_content = True
                content = base64.b64encode(response.raw.read())
            else:
                continue
        else:
            if not os.path.exists(path):
                sys.exit(path + ' does not exist')

            if not os.path.isfile(path):
                sys.exit(path + ' is not a file')

            content = open(path).read()

        if tag.name == 'link' and 'rel' in tag.attrs and tag['rel'] == 'stylesheet':
            process_css(path, html, tag, content)
        elif tag.name == 'script':
            process_script(tag, content)
        elif tag.name == 'img':
            process_img(path, tag, content)
        else:
            continue

    finalize(html)

    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'viewer')):
        os.makedirs(os.path.join(os.path.dirname(__file__), 'viewer'))

    f = open(os.path.join(os.path.dirname(__file__), 'viewer', sys.argv[name_index] + '.html'), 'w+')
    f.write(html.prettify('utf-8'))
    f.close()


def validate():
    if not FILE_PARAM in sys.argv:
        sys.exit('Please set the file parameter')

    index = sys.argv.index(FILE_PARAM) + 1

    if not any(p in sys.argv[index] for p in PROTOCOLS):
        if not os.path.exists(sys.argv[index]):
            sys.exit('File not found')

        if not os.path.isfile(sys.argv[index]):
            sys.exit('Path is not a file')

    if not NAME_PARAM in sys.argv:
        sys.exit('Please enter a name for the output file')

    name_index = sys.argv.index(NAME_PARAM) + 1

    if sys.argv[name_index] == '':
        sys.exit('Please enter a name for the output file')


def process_css(path, html, tag, content):
    global external

    sheet = cssutils.parseString(content)
    for rule in sheet:
        if not rule.type == rule.STYLE_RULE:
            continue

        for property in rule.style:
            if not 'url' in property.value:
                continue

            url = property.value.replace('url', CSS_SEPARATOR + 'url').replace('(', CSS_SEPARATOR).replace(')', CSS_SEPARATOR).split(CSS_SEPARATOR)
            url = url[url.index('url') + 1]
            if 'data:' in url:
                continue

            if external:
                img_path = urljoin(path, url)
            else:
                img_path = os.path.join(os.path.dirname(path), url)

            if any(p in img_path for p in PROTOCOLS):
                response = requests.get(img_path.replace('\\', '/'), stream=True)
                if response.status_code != 200:
                    sys.exit('Error while trying to retrieve external resource: ' + img_path + ' Response code: ' + str(
                        response.status_code))

                response.raw.decode_content = True
                img_content = base64.b64encode(response.raw.read())
            else:
                if not os.path.exists(img_path):
                    sys.exit(img_path + ' does not exist')

                if not os.path.isfile(img_path):
                    sys.exit(img_path + ' is not a file')

                img_content = base64.b64encode(open(img_path, 'rb').read())

            mimetype = mimetypes.types_map[os.path.splitext(img_path)[1]]
            img_content = 'data:' + mimetype + ';base64,' + img_content
            property.value = property.value.replace(url, img_content)

    style = html.new_tag('style', type='text/css')
    style.string = sheet.cssText
    tag.replace_with(style)


def process_script(tag, content):
    del tag['src']
    tag.string = content.replace('</script', '</scri\pt')


def process_img(path, tag, content):
    mimetype = mimetypes.types_map[os.path.splitext(path)[1]]
    tag['src'] = 'data:' + mimetype + ';base64,' + content


def finalize(html):
    styles = list()
    for style in html.find_all('style'):
        styles.append(style.string)
        style.extract()

    style = html.new_tag('style', type='text/css')
    style.string = ''.join(styles)
    html.head.append(style)


if __name__ == '__main__':
    main()
