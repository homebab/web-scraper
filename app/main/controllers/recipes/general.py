from flask import request
from flask_restx import Resource

from app.main.scrapers.general_recipes import MangaeRecipeScraper
from utils.logging import init_logger
from utils.s3_manager.manage import S3Manager

from flask_restx import Namespace

GeneralRecipe = Namespace(
    name="일반 레시피",
    description="scrape recipes on Recipe App Service(해먹남녀, 만개의 레시피)",
)


@GeneralRecipe.route('/mangae')
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
        self.bucket_name = 'omtm-production'
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


@GeneralRecipe.route('/haemuk')
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
        self.bucket_name = 'omtm-production'
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
