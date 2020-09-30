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

    def crawl(self):
        return dict()
