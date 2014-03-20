from collections import deque, OrderedDict

import miner.db
from items import UserItem, ProductItem, RatingItem


class Batch(object):
    MODELS = OrderedDict((
        (UserItem, miner.db.User),
        (ProductItem, miner.db.Product),
        (RatingItem, miner.db.Rating),
    ))

    BATCH_SIZE = 10000

    def __init__(self):
        self.current = 0
        self.batches = OrderedDict((k, deque()) for k in self.MODELS.keys())

    def add_item(self, item):
        self.batches[item.__class__].append(item)
        self.current += 1

        if self.current == self.BATCH_SIZE:
            self.commit()

    def commit(self):
        for klass, batch in self.batches.items():
            if len(batch) > 0:
                model = self.MODELS[klass]
                with miner.db.mysql.transaction():
                    model.insert_many(batch).execute()
                batch.clear()

        self.current = 0


class MySQLPipeline(object):
    def __init__(self):
        miner.db.init()
        self.batch = Batch()

    def process_item(self, item, spider):
        self.batch.add_item(item)

    def close_spider(self, spider):
        self.batch.commit()
