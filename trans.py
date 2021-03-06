#! /usr/bin/python3
import base64
import io
import os
import requests
import shutil
import sys
import xml.dom.minidom as xml
import yaml

rename = False
wm = base64.b64decode('RGFya09yYml0').decode("utf-8")
if sys.argv[1]:
    rename = True
    company = sys.argv[1]


class colors:
    red = '\033[91m'
    reset = '\033[0m'


dir = 'lang'
errors = []
languages = ['bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'hu',
             'it', 'ja', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk', 'sv', 'tr']
resources = ['resource_eic', 'resource_inventory', 'resource_achievement',
             'resource_chat', 'resource_loadingScreen', 'resource_items', 'flashres', 'resource_quest']
url = "https://%s-22.bpsecure.com/spacemap/templates/%s/" % (wm.lower(), dir)

if os.path.exists(dir):
    shutil.rmtree(dir)

if not os.path.exists('.cache'):
    os.makedirs('.cache')

if not os.path.exists(dir):
    os.makedirs(dir)


def write_to_file(file, trans):
    f = open(file, 'a+', encoding='utf8')
    keys = []

    for s in trans:
        index = s.attributes['name'].value

        if index in keys:
            continue

        if s.childNodes:
            value = s.childNodes[0].nodeValue
        else:
            value = '~'

        if rename:
            value = value.replace(wm.lower(), company.lower())
            value = value.replace(wm.upper(), company.upper())
            value = value.replace(wm.capitalize(), company.capitalize())
            value = value.replace(wm, company.capitalize())

        value = value.replace('\\"', '"')
        value = value.replace('"', '\\"')
        value = value.replace(u'\x98', '')
        value = value.replace(u'\x7f', '')
        value = '"%s"' % value

        if '"\\"' == value:
            value = '"\\\\"'

        if ',' == value:
            value = '","'

        value = value.replace('\n', ' ')
        f.write("%s: %s\n" % (index, value))
        keys.append(index)
    f.close()

    with open(file, 'r') as stream:
        try:
            yaml.load(stream)
            print("%s is valid" % file)
        except yaml.YAMLError as exc:
            sys.stdout.write("\r%serror occured for %s%s\n" %
                             (colors.red, file, colors.reset))
            errors.append({"err": exc, "file": file})


def prepare_file(slug, url):
    for language in languages:
        cached = ".cache/%s_%s.xml" % (slug, language)

        if not os.path.exists(cached):
            print('downloaded ', end='')
            r = requests.get(url.replace(dir, language))
            xml_file = io.StringIO(str(r.content, 'utf-8'))

            f = open(cached, 'a+', encoding='utf8')
            f.write(str(r.content, 'utf-8'))
            f.close()
        else:
            print('cached ', end='')
            f = open(cached, 'r', encoding='utf8')
            xml_file = io.StringIO(f.read())

        try:
            parsed_xml = xml.parse(xml_file)
            items = parsed_xml.getElementsByTagName('item')
            write_to_file("%s/%s.%s.yaml" % (dir, slug, language), items)
        except Exception as e:
            print(e)


for resource in resources:
    prepare_file(resource, "%s%s.xml" % (url, resource))

if len(errors):
    print('\n-------------------')
    for err in errors:
        print("\n%s%s%s\n%s" %
              (colors.red, err["file"], colors.reset, err["err"]))
