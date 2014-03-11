from scrapy.item import Item, Field

class UserItem(Item):
    uid = Field()
    uri = Field()
    age = Field()
    gender = Field()
    postcode = Field()

class ProductItem(Item):
    pid = Field()
    uri = Field()
    category = Field()
    name = Field()

class RatingItem(Item):
    uid = Field()
    pid = Field()
    score = Field()
    recommended = Field()
