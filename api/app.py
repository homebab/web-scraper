from flask import Flask, jsonify, request, render_template

from scrapers.categories import CoupangItemCategoriesScraper, HaemukItemCategoriesScraper
from scrapers.items import EmartItemScraper
from scrapers.recipes import MangaeRecipeScraper, HaemukRecipeScraper
from utils.logging import init_logger
from utils.s3_manager.manage import S3Manager


def main():
    logger = init_logger()

    app = Flask(__name__, template_folder='../static')
    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False

    bucket_name = "omtm-production"
    prefix = "scraper"

    # TODO: classify scrap recipe API service
    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/scrap-recipes/<source>', methods=['GET'])
    def scrap_recipes(source):
        """
        get recipes info for recipe recommendation
        :return: jsonified recipe
        """
        args = request.args
        try:
            str_num, end_num = args["str_num"], args["end_num"]
        except KeyError:
            logger.warning("There is no parameter, 'str_num' or 'end_num'")
            str_num, end_num = 6934386, 6934390

        logger.info("let's scrap {str} ~ {end} {source} recipes".format(str=str_num, end=end_num, source=source))

        key = "{prefix}/recipes/{source}".format(prefix=prefix, source=source)
        candidate_num = range(int(str_num), int(end_num))
        field = ['title', 'items', "duration", "tags"]

        if source == "mangae":
            result = MangaeRecipeScraper(
                base_url="https://www.10000recipe.com/recipe",
                candidate_num=candidate_num,
                field=field,
                bucket_name=bucket_name,
                key=key
            ).process()
        elif source == "haemuk":
            result = HaemukRecipeScraper(
                base_url="https://www.haemukja.com/recipes",
                candidate_num=candidate_num,
                field=field,
                bucket_name=bucket_name,
                key=key
            ).process()
        else:
            raise NotImplementedError

        return jsonify(result)

    @app.route('/scrap-items/<source>', methods=['GET'])
    def scrap_items(source):
        """
        get items info for food ingredients sales
        :return: jsonified items
        """
        logger.info("let's scrap {source} items".format(source=source))

        key = "{prefix}/items/{source}".format(prefix=prefix, source=source)
        head = True

        if source == "emart":
            result = EmartItemScraper(
                base_url="http://emart.ssg.com/",
                bucket_name=bucket_name,
                key=key,
                head=head
            ).process()
        else:
            raise NotImplementedError

        return jsonify(result)

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
                head=head
            ).process()
        elif source == "coupang":
            result = CoupangItemCategoriesScraper(
                base_url="https://www.coupang.com/np/categories/393760",
                bucket_name=bucket_name,
                key=key,
                head=head
            ).process()
        else:
            raise NotImplementedError

        return jsonify(result)

    @app.route('/<target>/<source>', methods=['GET'])
    def get(target, source):
        data = S3Manager(bucket_name=bucket_name).fetch_dict_from_json(
            key="{prefix}/{target}/{source}".format(prefix=prefix, target=target, source=source))
        if data is None:
            return 'there is no data'
        return jsonify(data)

    app.run(host='localhost', port=9000, debug=True)


if __name__ == '__main__':
    main()
