from collections import deque, OrderedDict

import miner.db
from items import UserItem, ProductItem, RatingItem


class Batch(object):
    """
    Structure used to stock chunks of items, in order to
    commit them to the database in transactions
    """
    MODELS = OrderedDict((
        (UserItem, miner.db.User),
        (ProductItem, miner.db.Product),
        (RatingItem, miner.db.Rating),
    ))

    # The number of items which will trigger a commit
    BATCH_SIZE = 10000

    def __init__(self):
        self.current = 0
        # We store three batches, one per model
        self.batches = OrderedDict((k, deque()) for k in self.MODELS.keys())

    def add_item(self, item):
        self.batches[item.__class__].append(item)
        self.current += 1

        if self.current == self.BATCH_SIZE:
            self.commit()

    def commit(self):
        # We commit the users and the products before the ratings
        # because the ForeignKeys must exist in the database
        for klass, batch in self.batches.items():
            if len(batch) > 0:
                model = self.MODELS[klass]
                with miner.db.mysql.transaction():
                    model.insert_many(batch).execute()
                batch.clear()

        self.current = 0


class MySQLPipeline(object):
    """
    The pipeline used to persist the items in the database
    """
    def __init__(self):
        miner.db.init()
        self.batch = Batch()

    def process_item(self, item, spider):
        self.batch.add_item(item)

    def close_spider(self, spider):
        # In the end, we commit the last items
        self.batch.commit()
