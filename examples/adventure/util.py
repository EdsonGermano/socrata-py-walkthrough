import logging
from termcolor import colored
import socrata

def interaction(title, choices):
    print('-' * 80)
    print(title)
    print('-' * 80)
    print(colored('Choose one of the following:', 'blue'))
    for i, (label, _) in enumerate(choices):
        print('[%s] %s' % (i, label))

    def accept():
        try:
            raw = input('Enter a number [0..%s]\n>>> ' % (len(choices)-1))
            return choices[int(raw)]
        except:
            print('Invalid choice', raw)
            return accept()


    (label, choice) = accept()
    print(colored('Running: %s' % label, 'red'))

    try:
        result = choice()
        if result == 'back':
            return
        elif result:
            (new_title, new_choices) = result
            return interaction(new_title, new_choices)

        interaction(title, choices)

    except Exception as e:
        print('Your data has been eaten by a grue')
        raise e


def back():
    return 'back'

def prompt(what):
    return input('%s\n>>> ' % what)

def setup_logging():
    logger = logging.getLogger(socrata.http.__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(colored('HTTP Request >>> %(message)s', 'green'))
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)



def dedent(s):
    return '\n'.join([l.strip() for l in s.split('\n')])
