from __future__ import print_function
import os
import sys
import logging
from argparse import ArgumentParser
import webbrowser
from notifyg import service

ENV_SOURCE = 'NOTIFYG_SOURCE'
ENV_SECRET = 'NOTIFYG_SECRET'
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
    parser.add_argument('--image-type', type=str, dest='image_type',
                        default=None,
                        help='MIME type of an image')
    parser.add_argument('--image-file', type=str, dest='image',
                        default=None,
                        help='Image file to send, "-" means stdin')
    parser.add_argument('--text-file', type=str, dest='text',
                        help='Text file to send, "-" means stdin')
    parser.add_argument('-v', dest='log_debug', action='store_true',
                        help='Verbose mode')
    parser.add_argument('message', metavar='MESSAGE', type=str, nargs='*',
                        help='Message to send')

    args = parser.parse_args()

    logging.basicConfig(level=get_log_level(args), format=LOG_FORMAT)

    source = None
    source_id = os.environ.get(ENV_SOURCE, None)
    secret = os.environ.get(ENV_SECRET, None)
    if source_id is None and not args.init:
        print('Environment {} is not set. Please perform `eval $(notifyg --init)`'.format(ENV_SOURCE),
              file=sys.stderr)
        sys.exit(1)
    if len(args.message) == 0 and not args.text and not args.image and not args.init:
        print('No messages to send', file=sys.stderr)
        sys.exit(1)
    if args.init:
        logger.info('Creating new source...')
        source = service.Source(name=args.name, secret=secret)
        if not args.no_browser:
            webbrowser.open(source.register_url)
        else:
            print('Please configure your notification source:',
                  source.register_url, file=sys.stderr)
        print('export {}={}'.format(ENV_SOURCE, source.id))
        print('export {}={}'.format(ENV_SECRET, source.secret))
    else:
        source = service.Source(id=source_id, secret=secret)
    image = None
    image_type = None
    message = None
    if args.image and args.image.strip() == '-':
        image_type = args.image_type
        image = sys.stdin.buffer
    elif args.image:
        image_type = args.image_type
        image = args.image
    elif args.text and args.text.strip() == '-':
        message = sys.stdin
    elif args.text:
        with open(args.text, 'r') as f:
            message = f.read()
    elif len(args.message) > 0:
        message = ' '.join(args.message)
    else:
        sys.exit(0)
    if image is not None:
        logger.info('Sending image...')
        source.send_image(image, image_type)
    elif message is not None:
        logger.info('Sending message... {}'.format(message))
        source.send(message)
    sys.exit(0)

if __name__ == '__main__':
    main()
