import miner.db
from items import UserItem, ProductItem, RatingItem

class Batch(object):
    def __init__(self, model, batch_size=10):
        self.model = model
        self.batch_size = batch_size
        self.batch = [None] * self.batch_size
        self.current = 0

    def add_item(self, item):
        self.batch[self.current] = item

        self.current += 1
        if self.current == self.batch_size:
            self.commit()

    def commit(self):
        if self.current == 0:
            return

        with miner.db.mysql.transaction():
            self.model.insert_many(self.batch[:self.current]).execute()

        self.current = 0


class MySQLPipeline(object):
    def __init__(self):
        miner.db.init()

        self.batches = {
            UserItem: Batch(miner.db.User),
            ProductItem: Batch(miner.db.Product),
            RatingItem: Batch(miner.db.Rating),
        }

    def process_item(self, item, spider):
        batch = self.batches[item.__class__]
        batch.add_item(item)

    def close_spider(self, spider):
        for batch in self.batches.values():
            batch.commit()
