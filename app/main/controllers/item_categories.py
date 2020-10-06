from flask import request, jsonify
from flask_restx import Resource, Namespace

from app.main.scrapers.item_categories import CoupangItemCategoriesScraper, HaemukItemCategoriesScraper
from utils.logging import init_logger

Category = Namespace(
    name="카테고리",
    description="scrape category structure on Grocery E-Commerce(로켓프레시), Recipe App Service(해먹남녀, 만개의 레시피)"
)


@Category.route('/')
class ItemCategory(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = init_logger()

        self.bucket_name = 'omtm-production'
        self.key = lambda s: "scraper/youtube_recipes/{source}.json".format(source=s)

    @Category.doc(params={
        'source': {
            'format': 'string',
            'description': 'haemuk or coupang'
        }
    })
    def get(self):
        """
        get item categories info for ingredients classification
        :return: jsonified recipe
        """
        source = request.args['source']

        self.logger.info("let's scrap {source} item categories".format(source=source))

        head = True

        if source == "haemuk":
            result = HaemukItemCategoriesScraper(
                base_url="https://www.haemukja.com/refrigerator",
                bucket_name=self.bucket_name,
                key=self.key,
                headless=head
            ).process()
        elif source == "coupang":
            result = CoupangItemCategoriesScraper(
                base_url="https://www.coupang.com/np/categories/393760",
                bucket_name=self.bucket_name,
                key=self.key,
                headless=head
            ).process()
        else:
            raise NotImplementedError

        return jsonify(result)
