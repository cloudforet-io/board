import factory
from spaceone.core import utils

from spaceone.board.model import Board


class BoardFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Board

    board_id = factory.LazyAttribute(lambda o: utils.generate_id("board"))
    name = factory.LazyAttribute(lambda o: utils.random_string())
    categories = ["a", "b", "c"]
    tags = {"x": "y"}
    created_at = factory.Faker("date_time")
