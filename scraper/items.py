from scrapy.item import Item, Field

class BaseItem(Item):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)

        for field in self.fields.keys():
            self.setdefault(field, None)

class UserItem(BaseItem):
    uid = Field()
    uri = Field()
    age = Field()
    gender = Field()
    postcode = Field()

class ProductItem(BaseItem):
    pid = Field()
    uri = Field()
    category = Field()
    name = Field()

class RatingItem(BaseItem):
    uid = Field()
    pid = Field()
    score = Field()
    recommended = Field()
