import os
import json
import cPickle as pickle

from .db import User, Rating, Product, init
from .apriori import apriori

minsup = 0.2
minconf = 0.75

panels = {
    "all": None,
    "men": User.gender == 'm',
    "men_20-30": User.gender == 'm' and User.age.between(20, 30),
    "men_30-80": User.gender == 'm' and User.age.between(30, 80),
    "women": User.gender == 'f',
    "women_20-30": User.gender == 'f' and User.age.between(20, 30),
    "women_30-80": User.gender == 'f' and User.age.between(30, 80),
}


def get_targets():
    t = {
        "recommended": Rating.recommended,
        "liked": Rating.score > 8,
        "disliked": Rating.score < 3
    }

    for category in ['film', 'jeuvideo', 'serie']:
        for name in ['recommended', 'liked', 'disliked']:
            t[name + "_" + category] = t[name] and Product.category == category

    return t

init()
for panel_name, panel in panels.items():
    users = User.select().where(panel)

    for target, criteria in get_targets().items():
        name = panel_name + "_" + target

        print name

        trans_file = "results/" + name + ".trans"
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

        rules = apriori(transactions, minsup, minconf, "results/" + name + ".freq")

        rules_export = []
        for rule, (conf, lift, leverage) in rules.items():
            l, r = ([Product.get(Product.pid == pid).name for pid in items] for items in rule)
            rules_export.append({'l': l, 'r': r, 'conf': conf, 'lift': lift, 'leverage': leverage})

        with open("results/" + name + ".json", 'w+') as f:
            output = {
                'minconf': minconf,
                'minsup': minsup,
                'rules': rules_export
            }
            json.dump(output, f, indent=2)
