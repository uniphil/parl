import re
from codecs import open
import requests
from lxml import html


SESSIONS = range(35, 41 + 1)


def session_debates(session):
    print('requesting...')
    index_url = 'http://parl.gc.ca/housechamberbusiness/ChamberSittings.aspx'
    index_params = dict(
        View='H',
        Language='E',
        Parl=session,
        Mode=2,  # text-mode
    )
    try:
        response = requests.get(index_url, params=index_params)
    except Exception as e:
        print 'SESSION DEBATES FAIL: {}'.format(e)
        return
    if response.status_code != 200:
        raise requests.HTTPError('did not get ok response')

    print('parsing...')
    id_re = r'.*DocId=(?P<id>\d+).*?'
    document = html.fromstring(response.text, base_url=index_url)
    for link in document.find_class('PublicationCalendarLink'):
        href = link.attrib['href']
        doc_id = re.match(id_re, href).groupdict()['id']
        yield doc_id


def get_debate(doc_id):
    print('getting debate {}...'.format(doc_id)),
    doc_url = 'http://parl.gc.ca/HousePublications/Publication.aspx'
    doc_params = dict(
        Language='E',
        mode='1',
        DocId=doc_id,
        xml='true',
    )
    try:
        response = requests.get(doc_url, params=doc_params)
    except Exception as e:
        print 'FAIL:\n{}'.format(e)
        return
    if response.status_code != 200:
        raise requests.HTTPError('did not get ok response.')

    print('saving')
    with open('xml/{}.xml'.format(doc_id), 'w', encoding='utf-8') as f:
        f.write(response.text)


if __name__ == '__main__':
    import multiprocessing
    p = multiprocessing.Pool(128)
    for session in SESSIONS:
        p.map(get_debate, session_debates(session))

