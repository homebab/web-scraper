from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from scrapers.ancestor import SeleniumScraper


class ItemCategoriesScraper(SeleniumScraper):
    """
        To crawl item categories

        - For Cooking
            Based on recipe providing service

        - For Shelf Life Management
            Based on online grocery shop
    """

    def __init__(self, base_url, bucket_name, key, headless):
        super().__init__(base_url, bucket_name, key, headless)

    def process(self) -> dict:
        """
            1. crawl items
            2. save to s3
            3. quit driver
        :return: items
        """
        items = self.crawl()
        # self.s3_manager.save_dict_to_json(
        #     data=items,
        #     key="{prefix}/{name}.json".format(prefix=self.prefix, name="item_categories")
        # )
        self.driver.quit()
        return items

    def crawl(self) -> dict:
        """
            1. connection
            2. get item_categories
        :return: item_categories
        """
        self.connection()
        return self.get_item_categories()

    def connection(self) -> None:
        self.driver.get(self.base_url)
        self.logger.debug("success to connect with '{url}'".format(url=self.base_url))

    def get_item_categories(self) -> dict:
        """
            event(click) <-> get_items
        """
        pass


class HaemukItemCategoriesScraper(ItemCategoriesScraper):
    """
        - Recipe Providing Service-
        https://www.haemukja.com/refrigerator

        parent - children
    """

    def __init__(self, base_url, bucket_name, key, headless):
        super().__init__(base_url, bucket_name, key, headless)

    def get_item_categories(self) -> dict:
        """
            parent:
                children
        :return: item categories
        """
        parents = self.driver.find_element_by_class_name('big_sort').find_elements_by_tag_name('a')

        def make_tuple(parent):
            parent.click()
            WebDriverWait(self.driver, 3).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, '//*[@id="container"]/div[2]/section/div/form/fieldset[1]/ul[2]/li')
                )
            )
            children = self.driver.find_element_by_class_name('small_sort').text.split("\n")

            return parent.text, children

        return dict(map(make_tuple, parents))


class CoupangItemCategoriesScraper(ItemCategoriesScraper):
    """
        - Online Grocery Shop -
        https://www.coupang.com/np/categories/393760


    """

    def __init__(self, base_url, bucket_name, key, headless):
        super().__init__(base_url, bucket_name, key, headless)

    def get_item_categories(self) -> dict:
        root = self.driver.find_element_by_id('searchCategoryComponent')
        container = []
        self.recursive(root, container)
        return

    def recursive(self, root, stack):
        stack.append(root.text.replace("\n열림", ""))
        print("stack: ", stack[1:])

        try:
            root = root.find_element_by_tag_name('ul')
        except NoSuchElementException:
            print('no ul element of root')
            stack.pop()
            return

        children = WebDriverWait(self.driver, 1).until(
            lambda driver: root.find_elements_by_tag_name('li')
        )
        for ele in children:
            try:
                WebDriverWait(self.driver, 5).until(
                    expected_conditions.element_to_be_clickable(By.TAG_NAME('a'))
                    # lambda driver: ele.find_element_by_tag_name('a')
                )
                ele.find_element_by_tag_name('a').click()
            except TimeoutException:
                print("no a tag of li")

            self.recursive(ele, stack)

        stack.pop()
