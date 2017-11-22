import io
import json
import urllib

import requests
from bs4 import BeautifulSoup

from pnapi import arraybuffer


class PnAPI:
    def __init__(self, dataset, user="", password="", endpoint="https://www.malariagen.net/panoptes"):
        self.dataset = dataset
        self.endpoint = endpoint
        self.session = requests.Session()
        domain = '/'.join(endpoint.split('/')[:3])
        config = self.session.get("{0.endpoint}/api?datatype=getconfig&dataset={0.dataset}".format(self))
        if config.status_code == 403:
            print("SSO login needed - attempting")
            cas_login_page = self.session.get("{0}?service={1.endpoint}/{1.dataset}/".format(config.json()['cas'], self))
            html = BeautifulSoup(cas_login_page.text, 'html.parser')
            fields = {e['name']: e.get('value', '') for e in html.find_all('input', {'name': True})}
            fields['username'] = user
            fields['password'] = password
            cas_login_response = self.session.post(domain + html.form['action'], data=fields)
            if "ail or password that you entered is incorrect" in cas_login_response.text:
                raise ConnectionRefusedError("BAD SSO Credentials")
            else:
                print('SSO Logged in')
        self.config = self._getconfig()

    def _getconfig(self):
        r = self.session.get("{0.endpoint}/api?datatype=getconfig&dataset={0.dataset}".format(self))
        return r.json()['config']

    def avaliableProperties(self):
        return {id: {prop['id']: prop['name'] for prop in t_conf['properties']} for id, t_conf in self.config['tablesById'].items()}

    def avaliable2DProperties(self):
        tables = self.config['twoDTablesById']
        return {id: {prop['id']: prop['name'] for prop in t_conf['properties']} for id, t_conf in tables.items()}

    def encodeB64(self, input):
        _keyStr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_='
        output = ''
        i = 0
        while i < len(input):
            chr1 = ord(input[i])
            i += 1
            try:
                chr2 = ord(input[i])
                i += 1
            except IndexError:
                chr2 = 0
            try:
                chr3 = ord(input[i])
                i += 1
            except IndexError:
                chr3 = 0

            enc1 = chr1 >> 2
            enc2 = ((chr1 & 3) << 4) | (chr2 >> 4)
            enc3 = ((chr2 & 15) << 2) | (chr3 >> 6)
            enc4 = chr3 & 63

            if chr2 is 0:
                enc3 = enc4 = 64
            elif chr3 is 0:
                enc4 = 64


            output = output + _keyStr[enc1] + _keyStr[enc2] + _keyStr[enc3] + _keyStr[enc4]
        return output

    def get2D(self, table, props, col_props, row_props, col_qry, row_qry, col_order, row_order, row_limit, row_offset):
        props = '~'.join(props)
        col_props = '~'.join(col_props)
        row_props = '~'.join(row_props)
        if col_qry is None:
            col_qry = '{"whcClass":"trivial","isCompound":false,"isTrivial":true,"Tpe":""}'
        if row_qry is None:
            row_qry = '{"whcClass":"trivial","isCompound":false,"isTrivial":true,"Tpe":""}'
        col_qry = self.encodeB64(col_qry)
        row_qry = self.encodeB64(row_qry)
        data = {
            'dataset': self.dataset,
            'table': table,
            '2DProperties': props,
            'colProperties': col_props,
            'rowProperties': row_props,
            'colQry': col_qry,
            'rowQry': row_qry,
            'rowOrder': row_order,
            'colOrder': col_order,
            'rowLimit': row_limit,
            'rowOffset': row_offset
        }
        params = urllib.parse.urlencode(data)
        r = self.session.get("{0.endpoint}/api?datatype=2d_query&dataset={0.dataset}&{1}".format(self, params), data=json.dumps(data))
        return arraybuffer.decode(io.BytesIO(r.content))

    def getQuery(self, table, columns, query=None):
        if query is None:
            query = '{"whcClass":"trivial","isCompound":false,"isTrivial":true,"Tpe":""}'
        data = {
            'database': self.dataset,
            'table': table,
            'columns': json.dumps(columns),
            'query': query,
        }
        r = self.session.post("{0.endpoint}/api?datatype=query".format(self), data=json.dumps(data))
        return arraybuffer.decode(io.BytesIO(r.content))

    def getGene(self, id):
        arrays = self.getQuery('annotation', ['fid', 'chromid', 'fname', 'fnames', 'descr', 'fstart', 'fstop', 'fparentid', 'ftype'],
                            '{"whcClass": "comparefixed", "isCompound": false, "ColName": "fid", "CompValue": "'+id+'", "Tpe": "="}')
        if len(arrays['fid']) != 1:
            raise LookupError('No gene found')
        else:
            return {'chrom': str(arrays['chromid'][0]), 'start': arrays['fstart'][0], 'stop': arrays['fstop'][0]}

    def getPropsForGene(self, geneId, table, props):
        gene = self.getGene(geneId)
        return self.getQuery(table, props, '{"whcClass":"compound","isCompound":true,"isRoot":true,"Components":[{"whcClass":"comparefixed","isCompound":false,"ColName":"POS","CompValue":'+str(gene['start']) + ',"Tpe":">="},{"whcClass":"comparefixed","isCompound":false,"ColName":"POS","CompValue":'+str(gene['stop']) + ',"Tpe":"<="},{"whcClass":"comparefixed","isCompound":false,"ColName":"CHROM","CompValue":"'+gene['chrom']+'","Tpe":"="}],"Tpe":"AND"}')
