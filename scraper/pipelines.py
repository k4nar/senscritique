from miner.db import User, Rate

class MySQLPipeline(object):
    def process_item(self, item, spider):
        return item
