from flask import Flask
from flask_restx import Api

from app.main.controllers.item_categories import Category
from app.main.controllers.recipes.general import GeneralRecipe
from app.main.controllers.recipes.youtube import Youtube


def create_app():

    file = open("app/main/description")
    description = file.read()
    file.close()

    app = Flask(__name__, template_folder='../static')
    api = Api(
        app,
        version='0.1.0',
        title="밥심 Scraper API",
        description=description,
        license="ⓒ 2020 TRAIN-J All rights reserved."
    )

    api.add_namespace(GeneralRecipe, '/recipes/general')
    api.add_namespace(Youtube, '/recipes/youtube')
    api.add_namespace(Category, '/categories')
    # api.add_namespace(Grocery, '/items')

    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False

    return app