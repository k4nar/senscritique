from collections import deque, OrderedDict

import miner.db
from items import UserItem, ProductItem, RatingItem


class MySQLPipeline(object):
    MODELS = OrderedDict((
        (UserItem, miner.db.User),
        (ProductItem, miner.db.Product),
        (RatingItem, miner.db.Rating),
    ))

    BATCH_SIZE = 10000

    def __init__(self):
        miner.db.init()

        self.current = 0
        self.batches = OrderedDict((k, deque()) for k in self.MODELS.keys())

    def process_item(self, item, spider):
        batch = self.batches[item.__class__]
        batch.append(item)

        self.current += 1
        if self.current == self.BATCH_SIZE:
            self.commit()

    def close_spider(self, spider):
        self.commit()

    def commit(self):
        for klass, batch in self.batches.items():
            if len(batch) > 0:
                model = self.MODELS[klass]
                with miner.db.mysql.transaction():
                    model.insert_many(batch).execute()
                batch.clear()

        self.current = 0
