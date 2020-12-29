import os
import sys
import logging
from argparse import ArgumentParser
import webbrowser
from notifyg import service

ENV_SOURCE = 'NOTIFYG_SOURCE'
LOG_FORMAT = '%(asctime)-15s %(levelname)s %(message)s'

logger = logging.getLogger()

def get_log_level(args):
    if args.log_debug:
        return logging.DEBUG
    else:
        return logging.WARN

def main():
    desc = 'Easy notification tool using notify.guru https://notify.guru'
    parser = ArgumentParser(description=desc)
    parser.add_argument('--init', dest='init', action='store_true',
                        help='Create new source and output environment {}'.format(ENV_SOURCE))
    parser.add_argument('--no-browser', dest='no_browser', action='store_true',
                        help='Prevent to open browser')
    parser.add_argument('-n', '--name', type=str, dest='name',
                        default=None,
                        help='Name of new source')
    parser.add_argument('--stdin', dest='stdin', action='store_true',
                        help='Send message from stdin')
    parser.add_argument('-v', dest='log_debug', action='store_true',
                        help='Verbose mode')
    parser.add_argument('message', metavar='MESSAGE', type=str, nargs='*',
                        help='Message to send')

    args = parser.parse_args()

    logging.basicConfig(level=get_log_level(args), format=LOG_FORMAT)

    source = None
    source_id = os.environ.get(ENV_SOURCE, None)
    if source_id is None and not args.init:
        print('Environment {} is not set. Please perform `eval $(notifyg --init)`'.format(ENV_SOURCE),
              file=sys.stderr)
        sys.exit(1)
    if len(args.message) == 0 and not args.stdin and not args.init:
        print('No messages to send', file=sys.stderr)
        sys.exit(1)
    if args.init:
        logger.info('Creating new source...')
        source = service.Source(name=args.name)
        if not args.no_browser:
            webbrowser.open(source.register_url)
        else:
            print('Please configure your notification source:',
                  source.register_url, file=sys.stderr)
        print('export {}={}'.format(ENV_SOURCE, source.id))
    else:
        source = service.Source(id=source_id)
    message = None
    if args.stdin:
        message = '\n'.join([line for line in sys.stdin])
    elif len(args.message) > 0:
        message = ' '.join(args.message)
    else:
        sys.exit(0)
    logger.info('Sending message... {}'.format(message))
    source.send(message)
    sys.exit(0)

if __name__ == '__main__':
    main()
