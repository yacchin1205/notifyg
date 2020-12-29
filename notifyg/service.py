import json
import os
import logging
import requests

SERVICE_URL = 'https://notify.guru/v1/sources/'

logger = logging.getLogger()

class Source:
    '''
    Notification Source of notify.guru

    Attributes
    ----------
    id : str
        ID of the source
    register_url : str
        URL to configure the source (Only when newly created)
    '''
    def __init__(self, id=None, name=None, service_url=None):
        '''
        An accessor for a source on notify.guru

        Parameters
        ----------
        id : str
            ID of an existing source (Optional)
            If id is not set, it will create new source on notify.guru.
        name : str
            Name of new source (Optional)
        service_url : str
            Service URL, like https://notify.guru/v1/sources/ (Optional)
        '''
        if id is not None:
            self.service_url = service_url or SERVICE_URL
            self.id = id
            self.register_url = None
        else:
            sourceinfo = {}
            if name is not None:
                sourceinfo['name'] = name
            self.service_url = service_url or SERVICE_URL
            resp = requests.put(self.service_url,
                                json=sourceinfo)
            resp.raise_for_status()
            sourcedata = resp.json()
            self.id = sourcedata['id']
            self.register_url = sourcedata['registerurl']

    def send(self, message):
        '''
        Send a message

        Parameters
        ----------
        message : str
            Message Text to send
        '''
        messagejson = message
        if isinstance(message, str):
            messagejson = {'text': message}
        logger.debug('Message: {}'.format(json.dumps(messagejson)))
        url = '{}{}/messages/'.format(self.service_url, self.id)
        resp = requests.put(url, json=messagejson)
        resp.raise_for_status()
