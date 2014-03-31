import os
import json
import cPickle as pickle

from .db import User, Rating, Product, init
from .apriori import apriori



# if os.path.exists('transactions'):
#     with open('transactions') as f:
#         transactions = pickle.load(f)
# else:
#     transactions = filter(None, (
#         frozenset(t[0] for t in user.rating_set.select(Rating.pid).join(Product).where(Rating.recommended and Product.category == 'film').tuples())
#         for user in User.select()
#     ))

#     with open('transactions', 'w+') as f:
#         pickle.dump(transactions, f, pickle.HIGHEST_PROTOCOL)

minsup = 0.2
minconf = 0.75

classes = {
    "all": User.select(),
    "men": User.select().where(User.gender == 'm'),
    "men_20-30": User.select().where(User.gender == 'm' and User.age.between(20, 30)),
    "men_30-80": User.select().where(User.gender == 'm' and User.age.between(30, 80)),
    "women": User.select().where(User.gender == 'f'),
    "women_20-30": User.select().where(User.gender == 'f' and User.age.between(20, 30)),
    "women_30-80": User.select().where(User.gender == 'f' and User.age.between(30, 80)),
}

def get_targets():
    targets = {
        "recommended": Rating.recommended,
        "liked": Rating.score > 8,
        "disliked": Rating.score < 3
    }

    for category in ['film', 'jeuvideo', 'serie']:
        for name in ['recommended', 'liked', 'disliked']:
            targets[name + "_" + category] = targets[name] and Product.category == category

    return targets

init()
for class_name, users in classes.items():
    users = users.execute()

    for target, criteria in get_targets().items():
        name = class_name + "_" + target

        print name

        trans_file = name + ".trans"
        if os.path.exists(trans_file):
            with open(trans_file) as f:
                transactions = pickle.load(f)
        else:
            transactions = filter(None, (
                set(t[0] for t in user.rating_set.select(Rating.pid).join(Product).where(criteria).tuples())
                for user in users
            ))

            with open(trans_file, 'w+') as f:
                pickle.dump(transactions, f, pickle.HIGHEST_PROTOCOL)

        rules = apriori(transactions, minsup, minconf, name + ".freq")

        output = []
        for rule, (conf, lift, leverage) in rules.items():
            l, r = ([Product.get(Product.pid == pid).name for pid in items] for items in rule)
            output.append({'l': l, 'r': r, 'conf': conf, 'lift': lift, 'leverage': leverage})

        with open(name + ".json", 'w+') as f:
            json.dump(output, f, indent=2)
