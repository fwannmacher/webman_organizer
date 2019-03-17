from sys import argv
from string import ascii_uppercase
from collections import OrderedDict
from xml.etree import ElementTree
from ftplib import FTP
from urllib import urlopen


WEBMANMOD_PATH = '/dev_hdd0/game/XMBMANPLS'
WEBMANMOD_IMAGES_PATH = '%s/USRDIR/IMAGES' % WEBMANMOD_PATH
FOLDER_ICON_PATH = '%s/filemanager.png' % WEBMANMOD_IMAGES_PATH
XML_FOLDER_PATH = '/dev_hdd0/xmlhost/game_plugin'


def parse_games(view):
    games = []

    for item in view.iter('Item'):
        games.append(item.attrib['key'])

    for table in view.iter('Table'):
        game = {'key': table.attrib['key'], 'table': table}

        for pair in list(table):
            game[pair.attrib['key']] = list(pair)[0].text

        game['title'] = game['title'].replace('%26', '&')

        for index, value in enumerate(games):
            if game['key'] == value:
                games[index] = game

                break
        else:
            raise KeyError()

    return games


def create_alphabet_folders_dict():
    alphabet_folders = OrderedDict()

    for character in '#%s' % ascii_uppercase:
        alphabet_folders[character] = []

    return alphabet_folders


def create_alphabet_table(segment, character, games):
    key = '%s_%s' % (segment.lstrip('seg_').rstrip('_items'), character)
    table = ElementTree.Element('Table', attrib={'key': key})
    pair = ElementTree.SubElement(table, 'Pair', attrib={'key': 'icon'})
    string = ElementTree.SubElement(pair, 'String')
    string.text = FOLDER_ICON_PATH
    pair = ElementTree.SubElement(table, 'Pair', attrib={'key': 'title'})
    string = ElementTree.SubElement(pair, 'String')
    string.text = character
    pair = ElementTree.SubElement(table, 'Pair', attrib={'key': 'info'})
    string = ElementTree.SubElement(pair, 'String')
    string.text = '%s games' % len(games)
    pair = ElementTree.SubElement(table, 'Pair', attrib={'key': 'str_notiem'})
    string = ElementTree.SubElement(pair, 'String')
    string.text = 'msg_error_no_content'

    return key, table


if __name__ == '__main__':
    with open('mygames.xml', 'wb') as file:
        ftp = FTP(argv[1])
        ftp.login()
        ftp.cwd(XML_FOLDER_PATH)
        ftp.retrbinary('RETR mygames.xml', file.write)
        ftp.close()

    with open('mygames.xml') as file:
        content = file.read()

    views = ElementTree.fromstring(content.replace('&', '%26')).findall('View')
    type_folders = {}

    for view in views[1:]:
        alphabet_folders = create_alphabet_folders_dict()
        type_folders[view.attrib['id']] = alphabet_folders

        for game in parse_games(view):
            first_character = game['title'][0].upper()

            if first_character in ascii_uppercase:
                alphabet_folders[first_character].append(game)
            else:
                alphabet_folders['#'].append(game)

    with open('mygames.xml', 'w') as file:
        xmbml = ElementTree.Element('XMBML', attrib={'version': '1.0'})
        xmbml.append(views[0])

        for segment, alphabet_folders in type_folders.iteritems():
            alphabet_view = ElementTree.Element('View', attrib={'id': segment})
            alphabet_attributes = ElementTree.SubElement(alphabet_view, 'Attributes')
            alphabet_items = ElementTree.SubElement(alphabet_view, 'Items')
            game_views = []

            for character, games in alphabet_folders.iteritems():
                if len(games) == 0:
                    continue

                key, table = create_alphabet_table(segment, character, games)
                folder_segment = 'seg_%s_items' % key
                alphabet_attributes.append(table)
                alphabet_items.append(ElementTree.Element(
                    'Query',
                    attrib={
                        'class': 'type:x-xmb/folder-pixmap',
                        'key': key,
                        'attr': key,
                        'src': "#%s" % folder_segment}))
                game_view = ElementTree.Element('View', attrib={'id': folder_segment})
                game_attributes = ElementTree.SubElement(game_view, 'Attributes')
                game_items = ElementTree.SubElement(game_view, 'Items')

                for game in games:
                    game_attributes.append(game['table'])
                    game_items.append(ElementTree.Element(
                        'Item',
                        attrib={
                            'class': 'type:x-xmb/module-action', 
                            'key': game['key'],
                            'attr': game['key']}))

                game_views.append(game_view)
            xmbml.append(alphabet_view)

            for game_view in game_views:
                xmbml.append(game_view)

        file.write(ElementTree.tostring(xmbml, encoding='UTF-8'))

    with open('mygames.xml', 'rb') as file:
        ftp = FTP(argv[1])
        ftp.login()
        ftp.cwd(XML_FOLDER_PATH)
        ftp.storbinary('STOR mygames.xml', file)
        ftp.close()

    urlopen('http://%s/restart.ps3' % argv[1]).read()
