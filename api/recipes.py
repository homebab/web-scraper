from flask import jsonify, request
from flask_restx import Namespace, Resource, abort

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.source = 'baek'
        self.logger = init_logger()

        self.bucket_name = 'omtm_production'
        self.key = "scraper/recipes/{source}".format(source=self.source)

    def get(self):
        """ get baek recipes from s3 """
        data = S3Manager(bucket_name=self.bucket_name).fetch_dict_from_json(key=self.key)
        if data is None:
            return 'there is no data'
        return data

    @Recipe.doc(params={
        'headless': {
            'format': '0 || 1',
            'description': '0(no) or 1(yes) - is chrome_driver headless'
        },
        'scrap_targets': {
            'format': '0 || 1',
            'description': '0(no) or 1(yes) - Does you scrap target urls'
        }
    })
    def post(self):
        """ scrape and upload baek recipes to s3 """
        args = request.args

        def validate_arg(key):
            try:
                value = args[key]
                if not (value == '1' or value == '0'):
                    abort(400, custom='[omtm]: {} should be 0 or 1'.format(key))
                return bool(int(args[key]))
            except KeyError:
                self.logger.debug('[omtm]: no query parameter, {}'.format(key))
                return None

        headless = validate_arg('headless')
        scrap_targets = validate_arg('scrap_targets')

        res = BaekRecipeScraper(
            base_url='https://www.youtube.com/playlist?list=PLoABXt5mipg4vxLw0NsRQLDDVBpOkshzF',
            bucket_name=self.bucket_name,
            key=self.key,
            headless=headless if headless else False,
            scrap_targets=scrap_targets if scrap_targets else False
        ).process()
        return 0


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
