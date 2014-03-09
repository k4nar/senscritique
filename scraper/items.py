from scrapy.item import Item, Field

class UserItem(Item):
    uri = Field()
    uid = Field()
    age = Field()
    gender = Field()
    postcode = Field()
