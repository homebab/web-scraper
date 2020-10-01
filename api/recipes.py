from flask import jsonify, request
from flask_restx import Namespace, Resource

from scrapers.general_recipes import MangaeRecipeScraper
from scrapers.youtube_recipes import BaekRecipeScraper
from utils.logging import init_logger
from utils.s3_manager.manage import S3Manager

Recipe = Namespace(
    name="Recipes",
    description="Scrape recipes on web",
)


@Recipe.route('/baek')
class BaekRecipe(Resource):
    def __init__(self, prefix, target, source, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.source = 'baek'

        self.bucket_name = 'omtm_production'
        self.key = "scraper/recipes/{source}".format(prefix=prefix, target=target, source=self.source)

    def get(self):
        """ get baek recipes from s3 """
        data = S3Manager(bucket_name=self.bucket_name).fetch_dict_from_json(key=self.key)
        if data is None:
            return 'there is no data'
        return data

    def post(self):
        """ scrape and upload baek recipes to s3 """
        res = BaekRecipeScraper(
            base_url='',
            bucket_name=self.bucket_name,
            key=self.key
        ).process()
        return res


@Recipe.route('/mangae')
class MangaeRecipe(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.source = 'mangae'
        self.logger = init_logger()

        args = request.args
        try:
            str_num, end_num = args["str_num"], args["end_num"]
        except KeyError:
            self.logger.warning("There is no parameter, 'str_num' or 'end_num'")
            str_num, end_num = 6934386, 6934390

        self.candidate_num = range(int(str_num), int(end_num))
        self.field = ['title', 'items', "duration", "tags"]
        self.bucket_name = 'omtm_production'
        self.key = "scraper/recipes/{source}".format(source=self.source)

    def get(self):
        data = S3Manager(bucket_name=self.bucket_name).fetch_dict_from_json(key=self.key)
        if data is None:
            return 'there is no data'
        return data

    def post(self):
        res = MangaeRecipeScraper(
            base_url="https://www.10000recipe.com/recipe",
            candidate_num=self.candidate_num,
            field=self.field,
            bucket_name=self.bucket_name,
            key=self.key
        ).process()

        return res


@Recipe.route('/haemuk')
class HaemukRecipe(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.source = 'haemuk'
        self.logger = init_logger()

        args = request.args
        try:
            str_num, end_num = args["str_num"], args["end_num"]
        except KeyError:
            self.logger.warning("There is no parameter, 'str_num' or 'end_num'")
            str_num, end_num = 5004, 5005

        self.candidate_num = range(int(str_num), int(end_num))
        self.field = ['title', 'items', "duration", "tags"]
        self.bucket_name = 'omtm_production'
        self.key = "scraper/recipes/{source}".format(source=self.source)

    def get(self):
        data = S3Manager(bucket_name=self.bucket_name).fetch_dict_from_json(key=self.key)
        if data is None:
            return 'there is no data'
        return data

    def post(self):
        res = MangaeRecipeScraper(
            base_url="https://www.10000recipe.com/recipe",
            candidate_num=self.candidate_num,
            field=self.field,
            bucket_name=self.bucket_name,
            key=self.key
        ).process()

        return res

#
# @app.route('/scrap-recipes/<source>', methods=['GET'])
#
#
# def scrap_recipes(source):
#     """
#     get recipes info for recipe recommendation
#     :return: jsonified recipe
#     """
#     args = request.args
#     try:
#         str_num, end_num = args["str_num"], args["end_num"]
#     except KeyError:
#         logger.warning("There is no parameter, 'str_num' or 'end_num'")
#         str_num, end_num = 6934386, 6934390
#
#     logger.info("let's scrap {str} ~ {end} {source} recipes".format(str=str_num, end=end_num, source=source))
#
#     key = "{prefix}/recipes/{source}".format(prefix=prefix, source=source)
#     candidate_num = range(int(str_num), int(end_num))
#     field = ['title', 'items', "duration", "tags"]
#
#     if source == "mangae":
#         result = MangaeRecipeScraper(
#             base_url="https://www.10000recipe.com/recipe",
#             candidate_num=candidate_num,
#             field=field,
#             bucket_name=bucket_name,
#             key=key
#         ).process()
#     elif source == "haemuk":
#         result = HaemukRecipeScraper(
#             base_url="https://www.haemukja.com/recipes",
#             candidate_num=candidate_num,
#             field=field,
#             bucket_name=bucket_name,
#             key=key
#         ).process()
#     else:
#         raise NotImplementedError
#
#     return jsonify(result)
