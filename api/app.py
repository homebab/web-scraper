from flask import Flask, jsonify, request, render_template
from flask_restx import Api

from api.recipes import Recipe
from scrapers.item_categories import HaemukItemCategoriesScraper, CoupangItemCategoriesScraper
from scrapers.item_price import EmartItemScraper
from scrapers.general_recipes import MangaeRecipeScraper, HaemukRecipeScraper
from utils.logging import init_logger
from utils.s3_manager.manage import S3Manager


def main():
    logger = init_logger()

    app = Flask(__name__, template_folder='../static')
    api = Api(
        app,
        version='0.1.0',
        title="한끼두끼 Scraper Api",
        description="scrape recipes, items, item_categories",
        terms_url="/",
        # contact="",
        license="MEOWAI"
    )

    api.add_namespace(Recipe, '/recipes')

    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False

    bucket_name = "omtm-production"
    prefix = "scraper"

    # TODO: classify scrap recipe API service
    @app.route('/scrap-item-categories/<source>', methods=['GET'])
    def get_item_categories(source):
        """
        get item categories info for ingredients classification
        :return: jsonified recipe
        """

        logger.info("let's scrap {source} item categories".format(source=source))

        key = "{prefix}/items/{source}".format(prefix=prefix, source=source)
        head = True

        if source == "haemuk":
            result = HaemukItemCategoriesScraper(
                base_url="https://www.haemukja.com/refrigerator",
                bucket_name=bucket_name,
                key=key,
                headless=head
            ).process()
        elif source == "coupang":
            result = CoupangItemCategoriesScraper(
                base_url="https://www.coupang.com/np/categories/393760",
                bucket_name=bucket_name,
                key=key,
                headless=head
            ).process()
        else:
            raise NotImplementedError

        return jsonify(result)

    # @app.route('/<target>/<source>', methods=['GET'])
    # def get(target, source):
    #     data = S3Manager(bucket_name=bucket_name).fetch_dict_from_json(
    #         key="{prefix}/{target}/{source}".format(prefix=prefix, target=target, source=source))
    #     if data is None:
    #         return 'there is no data'
    #     return jsonify(data)

    app.run(host='localhost', port=9000, debug=True)
