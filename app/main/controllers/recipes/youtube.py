import json

from flask import request
from flask_restx import Resource, abort, Namespace, fields

from app.main.scrapers.youtube import YoutubeDataAPIHandler, BaekRecipeScraper
from utils.encoder import DateTimeEncoder
from utils.logging import init_logger
from utils.s3_manager.manage import S3Manager

Youtube = Namespace(
    name="유튜브 레시피",
    description="scrape recipes on YouTube(백종원, 한끼두끼)",
)


@Youtube.route('')
class YoutubeRecipe(Resource):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.logger = init_logger()

        self.bucket_name = 'omtm-production'
        self.key = lambda s: "scraper/youtube_recipes/{source}".format(source=s)

    def validate_arg(self, key):
        try:
            return request.args[key]
        except KeyError:
            self.logger.debug('[omtm]: no query parameter')
            return None

    @Youtube.doc(params={
        'playlist-id': {
            'format': 'string',
            'description': 'youtube playlist id'
        }
    })
    def get(self):
        """ get youtube recipes from s3 """
        playlist_id = self.validate_arg(key='playlist-id')

        data = S3Manager(
            bucket_name=self.bucket_name
        ).fetch_dict_from_json(
            key=self.key(s=playlist_id if playlist_id else "")
        )
        if data is None:
            return 'there is no data'
        return data

    @Youtube.doc(params={
        'playlist-id': {
            'format': 'string',
            'description': 'youtube playlist id'
        }
    })
    def post(self):
        """ scrape and upload youtube recipes to s3 """

        playlist_id = self.validate_arg(key='playlist-id')
        if not playlist_id:
            raise KeyError

        res = YoutubeDataAPIHandler(
            bucket_name=self.bucket_name,
            key=self.key(s=playlist_id) + ".json"
        ).process(
            playlist_id=playlist_id
        )

        return json.dumps(res, cls=DateTimeEncoder, ensure_ascii=False)

# @YoutubeRecipe.route('/baek')
# class BaekRecipe(Resource):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.source = 'baek'
#         self.logger = init_logger()
#
#         self.bucket_name = 'omtm-production'
#         self.key = "scraper/recipes/{source}".format(source=self.source)
#
#     def get(self):
#         """ get baek recipes from s3 """
#         data = S3Manager(bucket_name=self.bucket_name).fetch_dict_from_json(key=self.key)
#         if data is None:
#             return 'there is no data'
#         return data
#
#     @YoutubeRecipe.doc(params={
#         'headless': {
#             'format': '0 || 1',
#             'description': '0(no) or 1(yes) - is chrome_driver headless'
#         },
#         'scrap_targets': {
#             'format': '0 || 1',
#             'description': '0(no) or 1(yes) - Does you scrap target urls'
#         }
#     })
#     def post(self):
#         """ scrape and upload baek recipes to s3 """
#         args = request.args
#
#         def validate_arg(key):
#             try:
#                 value = args[key]
#                 if not (value == '1' or value == '0'):
#                     abort(400, custom='[omtm]: {} should be 0 or 1'.format(key))
#                 return bool(int(args[key]))
#             except KeyError:
#                 self.logger.debug('[omtm]: no query parameter, {}'.format(key))
#                 return None
#
#         headless = validate_arg('headless')
#         scrap_targets = validate_arg('scrap_targets')
#
#         res = BaekRecipeScraper(
#             base_url='https://www.youtube.com/playlist?list=PLoABXt5mipg4vxLw0NsRQLDDVBpOkshzF',
#             bucket_name=self.bucket_name,
#             key=self.key,
#             headless=headless if headless else False,
#             scrap_targets=scrap_targets if scrap_targets else False
#         ).process()
#         return res
