from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from flask import current_app
from tempfile import NamedTemporaryFile
from pandas import read_csv
from tabulate import tabulate
import json


class Fuseki():
    def __init__(self):
        endpoint = current_app.config['FUSEKI_URL']
        self.store = SPARQLUpdateStore()
        self.query_endpoint = f"{endpoint}/query"
        self.update_endpoint = f"{endpoint}/update"
        self.store.open((self.query_endpoint, self.update_endpoint))

        self.remote_endpoint_list = current_app.config['REMOTE_URL_DICT']

    def query(self, sparql_query, format='html'):
        result = self.store.query(sparql_query)
        #current_app.logger.info(json.loads(result.serialize(format='json')))
        if format == 'html':
            result = self.__get_html(result)
        elif format == 'text':
            result = self.__get_text(result)
        elif format == 'json':
            result = json.loads(result.serialize(format='json'))

        current_app.logger.info(f"Result:\n{result}")
        return result

    def ask_local(self, ask_query):
        result = self.store.query(ask_query)
        result_json = json.loads(result.serialize(format='json'))
        return result_json['boolean']

    def ask_remote(self, remote_endpoint, ask_query):
        store = SPARQLUpdateStore()
        store.open(
            (f"{remote_endpoint}/query",
            f"{remote_endpoint}/update")
            )
        result = store.query(ask_query)
        result_json = json.loads(result.serialize(format='json'))
        return result_json['boolean']

    def ask_all(self, ask_query):
        result_list = []
        for endpoint, alias in self.remote_endpoint_list.items():
            result = self.ask_remote(endpoint, ask_query)
            if result:
                result_list.append(alias)
        current_app.logger.info(f"Available URL list:\n{result_list}")
        return result_list

    def __get_html(self, result):
        temp = NamedTemporaryFile()
        result.serialize(destination=temp.name, format='csv')
        df = read_csv(temp.name)
        temp.close()
        html = df.to_html(classes='table')
        return html

    def __get_text(self, result):
        temp = NamedTemporaryFile()
        result.serialize(destination=temp.name, format='csv')
        df = read_csv(temp.name)
        temp.close()
        table = tabulate(df, headers='keys', tablefmt='psql')
        return table