from abc import ABC

from scrapers.ancestor import SeleniumScraper


class ItemScraper(SeleniumScraper):
    def __init__(self, base_url, bucket_name, key, headless):
        super().__init__(base_url, bucket_name, key, headless)

    def process(self):
        raise NotImplementedError


class EmartItemScraper(ItemScraper, ABC):
    """
        - Online Grocery Shop -
         http://emart.ssg.com/

         grand parent - parent - children
    """

    def __init__(self, base_url, bucket_name, key, headless):
        super().__init__(base_url, bucket_name, key, headless)

