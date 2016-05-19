from glob import glob
from xml.dom import minidom
import xml.etree.ElementTree as ET
import pprint
import operator

from mailcase import MailCase

pp = pprint.PrettyPrinter(indent=4)

SPAM_PROB = 3./7.
HAM_PROB = 4./7.
SPAM_DICT = {}
HAM_DICT = {}


class SpamFilterData(object):
    def __init__(self):
        self.filter_data = {}

    def create_dictionary_from_xml(self, path):
        elements = self._get_data(self._get_dict_path(path))
        self._parse_data_and_fill_filter_data(elements)

    def print_database(self):
        pp.pprint(self.filter_data)

    def _parse_data_and_fill_filter_data(self, elements):
        for elem in elements:
            if isinstance(elem, minidom.Element):
                key = ET.fromstring(elem.toxml())
                key = key.findall(".")[0].text
                self.filter_data[key] = {
                    'type':         elem.attributes["type"].value,
                    'probability':  elem.attributes["probability"].value,
                }

    @staticmethod
    def _get_data(path):
        return minidom.parse(path).firstChild.childNodes

    @staticmethod
    def _get_dict_path(path):
        return glob(path)[0]


def spam_prob(spam_msg, msg):
    return spam_msg/msg


def laplace_smoothing(spam_msg, msg, k):
    return (spam_msg+k)/(msg+k*2)


def prepare_list_of_mails():
    paths = glob('./data/*txt')
    email_list = []
    map_red_list = []
    for path in paths:
        with open(path, encoding='windows-1250') as f:
            body = f.read()
            if 'spam' in path:
                _type = 'spam'
            elif 'ham' in path:
                _type = 'ham'
            else:
                _type = 'XXXXX'
            email_list.append(MailCase(body, _type))

    for mail in email_list:
        map_red_list.append((mail.reducer(), mail.type))
    return map_red_list


def count_prob(_type, body):
    occurring = set()
    ingredients = []

    for word in body:
        for each in _type:
            if each[0] in word:
                occurring.add(each[0])
    for each in _type:
        if each[0] in occurring:
            ingredients.append(float(each[1]))
        else:
            ingredients.append(1-float(each[1]))
    probability = 1
    for each in ingredients:
        probability *= each
    return probability


def words_in_spam(body, base):
    spam = [(k, v['probability']) for k, v in base.items() if v['type'] == 'spam']
    ham = [(k, v['probability']) for k, v in base.items() if v['type'] == 'ham']
    for k, v in SPAM_DICT.items():
        spam.append((k, v))
    for k, v in HAM_DICT.items():
        ham.append((k, v))
    spam = count_prob(spam, body)
    ham = count_prob(ham, body)
    print((spam*SPAM_PROB)/((spam*SPAM_PROB)+(ham*SPAM_PROB)))


def create_dict(body, counted=True):
    forbidden = ['odpowiedz', 'do', 'od',
                 'data', 'temat', 'treść', 'marca']
    temp = body[0].copy()
    if body[1] == 'spam':
        _DICT = SPAM_DICT
    elif body[1] == 'ham':
        _DICT = HAM_DICT
    else:
        _DICT = {}
    for each in body[0]:
        if each.isdigit():
            temp.pop(each, None)
        if each.lower() in forbidden:
            temp.pop(each, None)
    body = temp
    if counted:
        for k in body:
            if k in _DICT:
                _DICT[k] += 1
            else:
                _DICT[k] = 1
    return body


def final_prob():
    for k, v in SPAM_DICT.items():
        SPAM_DICT[k] = v/3
    for k, v in HAM_DICT.items():
        HAM_DICT[k] = v/4

if __name__ == "__main__":
    spam_data = SpamFilterData()
    spam_data.create_dictionary_from_xml('./data/*xml')
    mail_list = prepare_list_of_mails()
    new = {}
    for mail in mail_list:
        new = create_dict(mail, True)

    final_prob()
    sorted_x = sorted(SPAM_DICT.items(), key=operator.itemgetter(1))
    sorted_y = sorted(HAM_DICT.items(), key=operator.itemgetter(1))
    # pp.pprint(sorted_x)
    # pp.pprint(sorted_y)

    for mail in mail_list:
        new = create_dict(mail, False)
        print(mail[1])
        words_in_spam(new, spam_data.filter_data)