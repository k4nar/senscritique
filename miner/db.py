from pewee import MySQLDatabase, Model, CharField, ForeignKeyField, IntegerField, BooleanField

class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    uid = IntegerField(index=True, unique=True)
    uri = CharField(unique=True, max_length=16)
    age = IntegerField()
    gender = CharField(max_length=1)
    postcode = IntegerField()

class Product(BaseModel):
    pid = IntegerField(index=True, unique=True)
    uri = CharField(unique=True, max_length=64)
    category = CharField(max_length=1)
    name = CharField()

class Rate(BaseModel):
    uid = ForeignKeyField(User)
    pid = ForeignKeyField(Product)
    rate = IntegerField()
    recommended = BooleanField()
