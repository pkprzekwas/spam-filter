import re


class MailCase(object):
    u''' Simple box for holding mail body. '''
    def __init__(self, body, _type):
        self.body = body
        self.type = _type
        self.map_red = {}

    def print_body_of_mail(self):
        print(self.body)

    def return_body_of_mail(self):
        return self.body

    def mapper(self):
        words = sorted(self.body.split())
        return [(re.sub('[!:?,#$]', '', word.lower()), 1) for word in words]

    def reducer(self):
        words = self.mapper()
        current_word = None
        current_count = 0
        word = None

        for line in words:
            word, count = line[0], line[1]
            try:
                count = int(count)
            except ValueError:
                continue

            if current_word == word:
                current_count += count
            else:
                if current_word:
                    self.map_red[current_word] = current_count
                current_count = count
                current_word = word

        # do not forget to output the last word if needed!
        if current_word == word:
            self.map_red[current_word] = current_count
        return self.map_red
