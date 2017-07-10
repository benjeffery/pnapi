import requests
from bs4 import BeautifulSoup

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

    def get2D(self, table, props, col_qry, row_qry, col_order, row_order, col_props, row_props, colFailLimit=10000):
        
