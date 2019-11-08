import abc
import urllib3
import os
import re
from bs4 import BeautifulSoup


class Search(object):
    """
    This will act as base class for all search engines.
    """
    all_engines = {}

    @abc.abstractproperty
    def engine_name(self):
        return None

    @abc.abstractproperty
    def search_url(self):
        return None

    # Register all subclass against supported link_name
    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.all_engines[cls.engine_name] = cls

    def _prepare_search_url(self, query):
        return self.search_url.format(query)

    def search(self, query):
        url = self._prepare_search_url(query)
        http = urllib3.PoolManager()
        response = http.request(
            'GET',
            url,
            headers={'User-Agent': os.getenv('USER_AGENT')}
        )
        soup = BeautifulSoup(response.data, 'html.parser')
        extract_url = lambda x: re.split('=|&', x.get('href'))[1]
        all_urls = [extract_url(data) for data in soup.select('h3>a')]
        # remove invalid ruls
        all_urls = [url for url in all_urls if url.startswith('http')]
        return all_urls[:5]

    def execute(self, engine, query):
        return self.all_engines[engine]().search(query)

class Google(Search):
    engine_name = "google"
    # we are not considering any other parameter as of now.
    search_url = "https://www.google.com/search?q={}"
