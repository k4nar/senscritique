from miner.db import User, Product, Rating

class MySQLPipeline(object):
    def process_item(self, item, spider):
        return item
