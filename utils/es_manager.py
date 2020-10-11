from elasticsearch import Elasticsearch

from utils.logging import init_logger


class ESManager:
    """
        Elasticsearch Manager
    """

    def __init__(self):
        self.es = Elasticsearch('localhost:9200')
        NotImplemented()


if __name__ == '__main__':
    ESManager()
