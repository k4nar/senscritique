from peewee import (MySQLDatabase, Model, CharField,
                    ForeignKeyField, IntegerField, BooleanField)

mysql = MySQLDatabase('senscritique', user='root', passwd='root')


class BaseModel(Model):
    class Meta:
        database = mysql


class User(BaseModel):
    uid = IntegerField(primary_key=True)
    uri = CharField()
    age = IntegerField(null=True)
    gender = CharField(null=True)
    postcode = IntegerField(null=True)


class Product(BaseModel):
    pid = IntegerField(primary_key=True)
    uri = CharField()
    category = CharField()
    name = CharField()


class Rating(BaseModel):
    uid = ForeignKeyField(User)
    pid = ForeignKeyField(Product)
    score = IntegerField()
    recommended = BooleanField()


def init():
    """
    Connect to the database, and create the tables if necessary
    """
    mysql.connect()
    for model in [User, Product, Rating]:
        model.create_table(fail_silently=True)
