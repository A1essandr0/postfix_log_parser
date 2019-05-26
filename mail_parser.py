# Парсер для логов Postfix
# Будем понимать задачу так: для каждого отправителя (т.е. адреса email) учитывать письма, которые
# ему удалось / не удалось отправить
import re

log_file = open("maillog","r")

mail_id_pattern = re.compile(r'postfix\/\w{3,7}\[\d{3,6}\]: ([0-9A-F]{11}):')
sender_pattern = re.compile(r'from=<?([0-9A-Za-z._%+-]+@[0-9A-Za-z._-]+\.\w{2,5})>?')
recepient_pattern = re.compile(r' to=<?([0-9A-Za-z._%+-]+@[0-9A-Za-z._-]+\.\w{2,5})>?')
mail_status_pattern = re.compile(r'status=([a-z]{3,9})')
noqueue_pattern = re.compile(r'NOQUEUE')
# empty_from_pattern = re.compile(r'from=<>')
# wrong_from_pattern = re.compile(r'from=<>')
# wrong_to_pattern = re.compile(r'to=<>')

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



        # Добавим удаление ID из очереди после обработки

    else:
        # Отдельно обрабатывается случай, когда видим NOQUEUE вместо ID
        noque_match = noqueue_pattern.search(line)
        if noque_match:
            from_match = sender_pattern.search(line)
            if from_match:
                from_email = from_match[1]
                if from_email not in senders:
                    senders[from_email] = {'delivered': 0, 'failed': 0, 'recipients': []}
                senders[from_email]['failed'] += 1


outfile = open("senders.txt", "w")
for key, value in senders.items():
    print(key, "\n", value, "\n", file=outfile)

# Добавляем вывод в json

# outfile.close()
# log_file.close()
