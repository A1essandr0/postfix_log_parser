import re

patterns = {'mail_id': re.compile(r'postfix\/\w{3,7}\[\d{3,6}\]: ([0-9A-F]{11}):'),
            'sender': re.compile(r'from=<?([0-9A-Za-z._%+-]+@[0-9A-Za-z._-]+\.\w{2,5})>?'),
            'recepient': re.compile(r' to=<?([0-9A-Za-z._%+-]+@[0-9A-Za-z._-]+\.\w{2,5})>?'),
            'mail_status': re.compile(r'status=([a-z]{3,9})'),
            'noqueue': re.compile(r'NOQUEUE'),
            'removed': re.compile(r': removed'),
            'empty_from': '',
            'wrong_from': '',
            'wrong_to': ''
}

if __name__== "__main__":
    print("This is configuration script and shouldn't be run as standalone")