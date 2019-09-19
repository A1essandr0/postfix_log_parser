import unittest
from postfixlogparser import parse_postfix_log
from config import patterns

class TestPostfixParser(unittest.TestCase):

    def test_sent_immediately(self):
        correct_dict = {
            "t.ivanova@dalvl.ru": {
                "delivered": 1, 'failed': 0, 'recipients': ['elena_buh@krovinfo.ru']
                },
            "oksana_b@kubometr-samara.ru": {
                "delivered": 1, 'failed': 0, 'recipients': ['ninachekmeneva@mail.ru']
                },
            "VolodinV@echoavto.ru": {
                "delivered": 1, 'failed': 0, 'recipients': ['e.baklagenko@echoauto.ru']
                },
            "sclad@cement116.ru": {
                "delivered": 1, 'failed': 0, 'recipients': ['cembaza@mail.ru']
                },
        }
        with open("test_fixtures/sent_rightaway.txt", "r") as test_filename:
            self.assertEqual(parse_postfix_log(test_filename, patterns), correct_dict)

    def test_sent_after_delay(self):
        correct_dict = {
            "krasteplokomplekt@yandex.ru": {
                "delivered": 2, 'failed': 0, 'recipients': ['arsez24@rambler.ru', 'arsez@rambler.ru']
                },
            "roman@skgsk.ru": {
                "delivered": 1, 'failed': 0, 'recipients': ['malkina@pkdt.ru']
                },
        }
        with open("test_fixtures/sent_after.txt", "r") as test_filename:
            self.assertEqual(parse_postfix_log(test_filename, patterns), correct_dict)

    def test_greylisting_spam(self):
        correct_dict = {
            "krasteplokomplekt@yandex.ru": {
                "delivered": 0, 'failed': 1, 'recipients': []
                },
            "":     {
                "delivered": 1, 'failed': 0, 'recipients': ['krasteplokomplekt@yandex.ru']
                },
        }
        with open("test_fixtures/greylisting_spam.txt", "r") as test_filename:
            self.assertEqual(parse_postfix_log(test_filename, patterns), correct_dict)

    def test_mailbox_not_found(self):
        correct_dict = {
            "krasteplokomplekt@yandex.ru": {
                "delivered": 0, 'failed': 1, 'recipients': []
                },
            "":     {
                "delivered": 1, 'failed': 0, 'recipients': ['krasteplokomplekt@yandex.ru']
                },
            "r.ismiev@energomost-group.ru": {
                "delivered": 0, 'failed': 1, 'recipients': []
                },
        }
        with open("test_fixtures/error_mailbox_not_found.txt", "r") as test_filename:
            self.assertEqual(parse_postfix_log(test_filename, patterns), correct_dict)

    def test_expired(self):
        correct_dict = {
            "tduds@wmess.ru": {
                "delivered": 0, 'failed': 2, 'recipients': []
                },
        }
        with open("test_fixtures/error_expired.txt", "r") as test_filename:
            self.assertEqual(parse_postfix_log(test_filename, patterns), correct_dict)


if __name__== "__main__":
    unittest.main()