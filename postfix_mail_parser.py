# Парсер для логов Postfix
# Для каждого отправителя - т.е. адреса email - учитываем письма, которые ему удалось / не удалось отправить
import re
import json
import unittest


def parse_postfix_log(log_file, text_patterns):
    """
    Функция, получающая на вход итератор-текстовый файл и список паттернов в виде словаря регулярных выражений.
    Выдает словарь со статистикой отправлений.
    """
    mail_id_pattern, sender_pattern, recepient_pattern = patterns['mail_id'], patterns['sender'], patterns['recepient']
    mail_status_pattern, noqueue_pattern, removed_pattern = patterns['mail_status'], patterns['noqueue'], patterns['removed']

    id_table = {}   # активные id писем
    senders = {}    # список отправителей

    for line in log_file:
        id_match = mail_id_pattern.search(line)
        if id_match:    # Обрабатываем строку, если она содержит ID письма

            mail_id = id_match[1]
            if mail_id not in id_table:
                id_table[mail_id] = {'from': '', 'to': ''}

            from_match = sender_pattern.search(line)
            if from_match:  # Если строка содержит поле from
                from_email = from_match[1]
                id_table[mail_id]['from'] = from_email
                if from_email not in senders:
                    senders[from_email] = {'delivered': 0, 'failed': 0, 'recipients': []}

                status_match = mail_status_pattern.search(line)
                if status_match and status_match[1] == 'expired':
                    senders[from_email]['failed'] += 1

            # else: # Можно обработать случаи пустого или некорректного from:, посчитал ненужным

            to_match = recepient_pattern.search(line)
            if to_match:    # Если строка содержит поле to
                to_email = to_match[1]
                from_email = id_table[mail_id]['from']
                id_table[mail_id]['to'] = to_email

                status_match = mail_status_pattern.search(line)
                # Если статус=deferred, ничего делать не нужно

                if status_match and status_match[1] == 'sent':  # Если письмо отправлено
                    if from_email not in senders:
                        senders[from_email] = {'delivered': 0, 'failed': 0, 'recipients': []}

                    senders[from_email]['delivered'] += 1
                    senders[from_email]['recipients'].append(to_email)

                elif status_match and status_match[1] == 'bounced': # Если письмо отфутболено
                    senders[from_email]['failed'] += 1

            # else: # Можно обработать случай некорректного to:, посчитал ненужным

            removed_match = removed_pattern.search(line)
            if removed_match: # Добавим удаление ID из очереди после обработки
                del id_table[mail_id]

        else:   # Отдельно обрабатывается случай, когда видим NOQUEUE вместо ID
            noque_match = noqueue_pattern.search(line)
            if noque_match:
                from_match = sender_pattern.search(line)
                if from_match:
                    from_email = from_match[1]
                    if from_email not in senders:
                        senders[from_email] = {'delivered': 0, 'failed': 0, 'recipients': []}
                    senders[from_email]['failed'] += 1

    return senders


def postfix_log_to_json(senders_obj, file):
    """
    Функция, отправляющая словарь со статистикой в json файл
    """
    outfile = open(file,"w")
    json_object = json.dumps(senders_obj, sort_keys=True, indent=4)
    print(json_object, file=outfile)
    outfile.close()


log = open("mlog","r")

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

log_statistics = parse_postfix_log(log, patterns)
log.close()

postfix_log_to_json(senders_obj=log_statistics, file="senders.json")
