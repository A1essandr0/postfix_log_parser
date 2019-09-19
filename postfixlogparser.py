#!/usr/bin/env python3 
# Log file parser for Postfix email server
# For every sender email it collects all recepients' emails and counts delivered/failed messages
# Outputs to nice json

import json
import argparse
from config import patterns


def parse_postfix_log(log_file, text_patterns):
    """
    Takes iterator and dict with regexp patterns.
    Outputs dict with statistics of email deliveries.
    """
    mail_id_pattern     = text_patterns['mail_id']
    sender_pattern      = text_patterns['sender'] 
    recepient_pattern   = text_patterns['recepient']
    mail_status_pattern = text_patterns['mail_status'] 
    noqueue_pattern     = text_patterns['noqueue']
    removed_pattern     = text_patterns['removed']

    # Dictionary with active id's  { <ID>: {
    #                                   'from': <from_email>, 
    #                                    'to': <to_email> 
    #                                         }, ...,  
    #                                 }
    id_table = {}

    # Function output:             { <from_email>: 
    #                                       {'delivered': a, 
    #                                        'failed': b, 
    #                                        'recipients': [email1, email2, ...] 
    #                                       }, ...,
    #                                   }
    senders = {}


    for line in log_file:

        # Если строка содержит ID письма, обрабатываем ее, иначе - игнорируем
        id_match = mail_id_pattern.search(line)
        if id_match:

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
                    del id_table[mail_id] # Удаление ID письма из очереди

            # else: # Можно обработать случаи некорректного from:

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

            # else: # Можно обработать случаи некорректного to:

            removed_match = removed_pattern.search(line)
            if removed_match: # Удаление ID письма из очереди после обработки
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


def dict_to_json(senders_obj, file):
    """
    Saves dictionary as json
    """
    outfile = open(file, "w")
    json_object = json.dumps(senders_obj, sort_keys=True, indent=4)
    print(json_object, file=outfile)
    outfile.close()


if __name__== "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("filename", help="Postfix log file to parse")
    argparser.add_argument("output", help="File to put json data into")
    args = argparser.parse_args()

    with open(args.filename, "r") as log:
        log_statistics = parse_postfix_log(log, patterns)

    dict_to_json(senders_obj=log_statistics, file=args.output)
    print("File {0} parsed, stats put in {1}".format(args.filename, args.output))
