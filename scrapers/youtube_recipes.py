from scrapers.ancestor import SeleniumScraper


class YoutubeRecipeScraper(SeleniumScraper):
    """
        {
            name: string,
            avatar_url: string,
            recipes: [
                {
                    id: string,
                    name: string,
                    description: string,
                    views: number,
                    tags: Array<string>,
                    uploaded_at: Date,
                    thumbnail_url: string
                }
            ]
        }

        id -> base_url, embed_url, -image_url-

            base_url: https://www.youtube.com/watch?v={id}
            embed_url: https://www.youtube.com/embed/{id}
            -thumbnail_url: https://i.ytimg.com/{id}/default.jpg-
    """
    def __init__(self, base_url, bucket_name, key):
        super().__init__(base_url, bucket_name, key)

    def process(self) -> dict:
        """
            1. crawl recipes
            2. save to s3
            3. quit driver
        :return: items
        """
        recipes = self.crawl()
        # self.s3_manager.save_dict_to_json(
        #     data=items,
        #     key="{prefix}/{name}.json".format(prefix=self.prefix, name="item_categories")
        # )
        self.driver.quit()
        return recipes

    def crawl(self) -> dict:
        """
            1. connection
            2. get recipes
        :return: item_categories
        """
        self.connection()
        return self.get_recipes()

    def connection(self) -> None:
        self.driver.get(self.base_url)
        self.logger.debug("success to connect with '{url}'".format(url=self.base_url))

    def get_recipes(self) -> dict:
        """
            event(click) <-> get_items
        """
        pass


class BaekRecipeScraper(YoutubeRecipeScraper):
    def __init__(self, base_url, bucket_name, key):
        """
        :param base_url: 'https://www.youtube.com/watch?v=v32NjYn5pSc&list=PLoABXt5mipg4vxLw0NsRQLDDVBpOkshzF&index=1'
        :param bucket_name: 'omtm-app-service
        :param key:
        """
        super().__init__(base_url, bucket_name, key)

        def get_recipes(self) -> dict:
            return dict()


