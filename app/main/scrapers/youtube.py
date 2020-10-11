import json
import os
import uuid
from datetime import datetime
from functools import reduce
from time import sleep

import requests
from flask_restx import abort
from joblib import dump, load
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from app.main.scrapers.ancestor import SeleniumScraper
from utils.encoder import DateTimeEncoder
from utils.s3_manager.manage import S3Manager


class YoutubeRecipeScraper(SeleniumScraper):
    """
        {
            id: UUID,
            external_id: string,
            title: string,
            description: string,
            views: number,
            tags: Array<string>,
            source_url: string,
            # thumbnail_url: string,
            owner: string,
            avatar_url: string
        }

        As using external_id, you can make base_url, embed_url, -image_url-

            in case of youtube()
            base_url: https://www.youtube.com/watch?v={external_id}
            embed_url: https://www.youtube.com/embed/{external_id}
            -thumbnail_url: https://i.ytimg.com/{external_id}/default.jpg-
    """

    def __init__(self, base_url, bucket_name, key, headless):
        super().__init__(base_url, bucket_name, key, headless)

    def process(self) -> dict:
        """
            1. crawl recipes
            2. save to s3
            3. quit driver
        :return: items
        """
        try:
            data = self.crawl()
            self.s3_manager.save_dict_to_json(
                data=data,
                key="{prefix}/{name}.json".format(prefix=self.prefix, name="youtube-{}".format(data['owner']))
            )
            self.driver.quit()
            return data
        except Exception as e:
            self.logger.exception(e, exc_info=True)
            self.driver.quit()
            abort(400, custom='[omtm]: the selenium exits with error, {}'.format(e))

    def crawl(self) -> dict:
        """
            1. connection
            2. get recipes
        :return: item_categories
        """
        return self.get_recipes()

    def connection(self, url=None) -> None:
        target_url = url if url else self.base_url
        self.driver.get(target_url)
        self.logger.debug("[omtm]: success to connect with '{url}'".format(url=target_url))

    def get_recipes(self) -> dict:
        """
            event(click) <-> get_items
        """
        pass

    def make_dict(self):
        return {
            'id': self.get_id(),
            'external_id': self.get_external_id(),
            'title': self.get_title(),
            'description': self.get_description(),
            'views': self.get_views(),
            'tags': self.get_tags(),
            'owner': self.get_owner(),
            'avatar_url': self.get_avatar_url()
        }

    @staticmethod
    def get_id():
        return uuid.uuid4()

    def get_external_id(self):
        return self.driver.current_url.split('?v=')[1].split('&')[0]

    def get_title(self):
        return self.driver.find_element_by_xpath('//*[@id="container"]/h1/yt-formatted-string').text

    def get_description(self):
        return self.driver.find_element_by_xpath('//*[@id="description"]/yt-formatted-string/span[3]').text

    def get_views(self):
        text = self.driver.find_element_by_xpath('//*[@id="count"]/yt-view-count-renderer/span[1]').text
        return int(''.join(filter(lambda c: c.isdigit(), text)))

    def get_tags(self):
        elements = self.driver.find_elements_by_xpath('//*[@id="container"]/yt-formatted-string/a')
        return list(map(lambda e: e.text, elements))

    def get_owner(self):
        return self.driver.find_element_by_xpath('//*[@id="text"]/a').text

    def get_avatar_url(self):
        return self.driver.find_element_by_xpath('//*[@id="img"]').get_attribute('src')


class BaekRecipeScraper(YoutubeRecipeScraper):
    def __init__(self, base_url, bucket_name, key, headless, scrap_targets=False):
        """
        :param base_url: 'https://www.youtube.com/playlist?list=PLoABXt5mipg4vxLw0NsRQLDDVBpOkshzF' - playlist
        :param bucket_name: 'omtm-production'
        :param key:
        """
        super().__init__(base_url, bucket_name, key, headless)

        if scrap_targets:
            self.connection()
            try:
                self.targets = self.save_targets()
            except Exception as e:
                self.logger.exception(e, exc_info=True)
                self.driver.quit()
                abort(400, custom='[omtm]: the selenium exits with error, {}'.format(e))
        else:
            self.targets = load('resources/targets')

    def save_targets(self):
        html = None

        for _ in range(3):
            # scroll down three time
            html = self.driver.find_element_by_tag_name('html')
            html.send_keys(Keys.END)

            # TODO: not to be ambiguous
            sleep(3)

        recipe_elements = html.find_elements_by_xpath(
            '//*[@id="contents"]/ytd-playlist-video-renderer')  # html.find_elements_by_id('thumbnail')
        owner_element = html.find_element_by_id('owner-container')

        targets = list(filter(
            lambda url: None not in url, map(
                lambda ele: {
                    'source_url': ele.find_element_by_tag_name('a').get_attribute("href"),
                    'owner': owner_element.find_element_by_id('upload-info').text,
                    'avatar_url': owner_element.find_element_by_id('avatar').find_element_by_id('img').get_attribute(
                        'src')
                },
                recipe_elements
            )))
        dump(targets, 'resources/targets')

        self.logger.debug('[omtm]: success to save targets on local, {}'.format(targets))
        return targets

    def get_recipe(self, target) -> dict or None:
        self.connection(target["source_url"])

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, '//*[@id="description"]/yt-formatted-string/span[3]')
            )
        )

        merged = {**self.make_dict(), **target}
        self.logger.debug('[omtm]: scrape a recipe, {}'.format(merged))
        return merged

    def get_recipes(self) -> dict:
        """
            1. get all target url
                - retrieve target urls or scrap again
            2. mapReduce
                2-1. get a recipe from each target url
                2-2. reduce all recipes

        :return:
        """

        result = filter(lambda d: None not in d, map(self.get_recipe, self.targets))

        # with mp.Pool(mp.cpu_count()) as p:
        #     result = p.map(self.worker, targets)

        # reduced = list(reduce(lambda l, r: l + r, result))
        return {
            'platform': 'youtube',
            'owner': self.targets[0]['owner'],
            'uploaded_at': datetime.now(),
            'recipes': list(result)
        }


class YoutubeDataAPIHandler:
    """
        Youtube Data API - 'https://developers.google.com/youtube/v3/docs'

        Response Type:
        {
          "kind": "youtube#playlistItemListResponse",
          "etag": etag,
          "nextPageToken": string,
          "prevPageToken": string,
          "pageInfo": {
            "totalResults": integer,
            "resultsPerPage": integer
          },
          "items": [
            playlistItem Resource - 'https://developers.google.com/youtube/v3/docs/playlistItems#resource'
          ]
        }

    """

    def __init__(self, bucket_name, key):
        self.base_url = 'https://www.googleapis.com/youtube/v3'
        self.s3_manager = S3Manager(bucket_name=bucket_name)
        self.key = key

        pass

    def process(self, playlist_id, youtube_api_key=None):
        """
            1. fetch items on the playlist from Youtube
            2. transform response
            3. upload to S3
        :return:
        """
        items = self.fetch_playlist_items(playlist_id=playlist_id, youtube_api_key=youtube_api_key)
        transformed = list(map(self.transform, items))
        # data = {
        #     'created_at': datetime.now(),
        #     'total_num': len(transformed),
        #     'data': transformed
        # }
        self.s3_manager.save_dict_to_json(transformed, key=self.key, encoder=DateTimeEncoder)
        return transformed

    @staticmethod
    def transform(item):
        """
        Input Item Type: 'https://developers.google.com/youtube/v3/docs/playlistItems#resource'
        {
          "kind": "youtube#playlistItem",
          "etag": etag,
          "id": string,
          "snippet": {
            "publishedAt": datetime,
            "channelId": string,
            "title": string,
            "description": string,
            "thumbnails": {
              (key): {
                "url": string,
                "width": unsigned integer,
                "height": unsigned integer
              }
            },
            "channelTitle": string,
            "playlistId": string,
            "position": unsigned integer,
            "resourceId": {
              "kind": string,
              "videoId": string,
            }
          }
        }
        :return: {
            id: UUID,
            videoId -> external_id: string,
            title: string,
            description: string
            thumbnails: Array,
            publishedAt -> published_at: datetime,
            channelTitle -> publisher: string,
            kind: 'youtube#video'
        }
        """
        result = dict()
        snippet = item['snippet']
        result['kind'] = 'youtube#video'
        result['external_id'] = snippet['resourceId']['videoId']
        result['published_at'] = snippet['publishedAt']
        result['publisher'] = snippet['channelTitle']
        result['title'] = snippet['title']
        result['description'] = snippet['description']
        result['thumbnails'] = snippet['thumbnails']

        return result

    def fetch_playlist_items(self, playlist_id, youtube_api_key=None, part='snippet', next_page_token='default'):
        items = []
        while next_page_token:
            response = requests.get(
                self.base_url + '/playlistItems',
                params={
                    'part': part,
                    'playlistId': playlist_id,
                    'maxResults': 50,
                    'key': youtube_api_key if youtube_api_key else os.environ['YOUTUBE_API_KEY']
                } if next_page_token == 'default' else {
                    'part': part,
                    'playlistId': playlist_id,
                    'maxResults': 50,
                    'pageToken': next_page_token,
                    'key': youtube_api_key if youtube_api_key else os.environ['YOUTUBE_API_KEY']
                }
            ).json()

            items.append(response['items'])
            try:
                next_page_token = response['nextPageToken']
            except KeyError:
                next_page_token = None

        return reduce(lambda l, r: l + r, items)


if __name__ == '__main__':
    # res = fetch_playlist(playlist_id='PLoABXt5mipg4vxLw0NsRQLDDVBpOkshzF')
    # print(res)


    a = {}
    b = {1: 2}
    c = {3: 4}
    print({5: 6, **b, **a})
    if {}:
        print('yes')
