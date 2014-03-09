from scrapy.item import Item, Field

class UserItem(Item):
    name = Field()
    uid = Field()
    age = Field()
    gender = Field()
