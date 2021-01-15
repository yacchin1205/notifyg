from datetime import datetime
import json
import os
import logging
import hashlib
import hmac
import requests
import six

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
    def __init__(self, id=None, secret=None, name=None, service_url=None):
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
            if secret is None:
                raise ValueError('secret is not set')
            self.service_url = service_url or SERVICE_URL
            self.id = id
            self.secret = secret
            self.register_url = None
        else:
            sourceinfo = {}
            if name is not None:
                sourceinfo['name'] = name
            if secret is not None:
                sourceinfo['secret'] = secret
            self.service_url = service_url or SERVICE_URL
            resp = requests.put(self.service_url,
                                json=sourceinfo)
            resp.raise_for_status()
            sourcedata = resp.json()
            self.id = sourcedata['id']
            self.secret = sourcedata['secret']
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
        if isinstance(message, six.string_types):
            messagejson = {'text': message}
        elif hasattr(message, 'read'):
            messagejson = {'text': message.read()}
        logger.debug('Message: {}'.format(json.dumps(messagejson)))
        data = json.dumps(messagejson).encode('utf8')
        self._send('application/json; charset=utf-8', data)

    def send_image(self, image, mime_type=None):
        '''
        Send an image

        Parameters
        ----------
        image : str or file
            An Image to send
        mime_type : str
            A MIME type to send
        '''
        data = None
        if isinstance(image, six.string_types):
            with open(image, 'rb') as f:
                data = f.read()
        elif hasattr(image, 'read'):
            data = image.read()
        else:
            raise ValueError('Unexpected value')
        if mime_type is None:
            import magic
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(data)
        self._send(mime_type, data)

    def _send(self, content_type, data):
        '''
        Send a message

        Parameters
        ----------
        data : bytes
            Message Payload to send
        '''
        url = '{}{}/messages/'.format(self.service_url, self.id)
        hash = hashlib.sha256()
        hash.update(data)
        headers = {
            'Content-Type': content_type,
            'Host': 'notify.guru',
            'x-notifyg-epoch': str(int(datetime.now().timestamp() * 1000)),
            'x-notifyg-content-sha256': hash.hexdigest(),
        }
        signature = self._compute_signature('PUT', url, {}, headers, data)
        logger.debug('Signature: {}'.format(signature))
        headers['Authorization'] = signature
        resp = requests.put(url, headers=headers, data=data)
        resp.raise_for_status()

    def _compute_signature(self, method, url, queries, headers, data):
        # Canonical Request = HTTP Verb + '\n' +
        # Canonical URI + '\n' + Canonical Query String + '\n' +
        # Canonical Headers + '\n' + Signed Headers
        # StringToSign = 'NOTIFYG-HMAC-SHA256' + '\n' + EpochTime + '\n' +
        # Hex(SHA256Hash(Canonical Request))
        # SigningKey = Hex(HMAC-SHA256(Secret, 'NOTIFYG-202101'))
        # Signature = Hex(HMAC-SHA256(SigningKey, StringToSign))
        canonical_request = method + '\n' + url + '\n'
        querykeys = sorted(queries.keys())
        canonical_query_string = '&'.join(['{}={}'.format(requests.utils.quote(key),
                                                          requests.utils.quote(queries[key]))
                                           for key in querykeys])
        canonical_request += canonical_query_string + '\n'
        headercands = {'host', 'content-type', 'x-notifyg-epoch', 'x-notifyg-content-sha256'}
        headerkeys = sorted([k for k in headers.keys() if k.lower() in headercands],
                            key=lambda x: x.lower())
        canonical_headers = '\n'.join(['{}:{}'.format(key.lower(), headers[key].strip())
                                       for key in headerkeys])
        canonical_request += canonical_headers + '\n'
        canonical_request += ';'.join([k.lower() for k in headerkeys])
        logger.debug('CanonicalRequest: {}'.format(canonical_request))
        hash = hashlib.sha256()
        hash.update(canonical_request.encode('utf8'))
        string_to_sign = 'NOTIFYG-HMAC-SHA256\n' + headers['x-notifyg-epoch'] + '\n' + hash.hexdigest()
        logger.debug('StringToSign: {}'.format(string_to_sign))
        signing_key = hmac.new(self.secret.encode('utf8'), digestmod=hashlib.sha256)
        signing_key.update(b'NOTIFYG-202101')
        logger.debug('SigningKey: {}'.format(signing_key.hexdigest()))
        signature = hmac.new(signing_key.hexdigest().encode('utf8'), digestmod=hashlib.sha256)
        signature.update(string_to_sign.encode('utf8'))
        return signature.hexdigest()
