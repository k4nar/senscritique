import os
import json
import cPickle as pickle

from .db import User, Rating, Product, init
from .apriori import apriori

minsup = 0.1
minconf = 0.8

panels = {
    "all": None,
    "men": User.gender == 'm',
    "women": User.gender == 'f',
    "oldest": User.age > 25,
    "youngest": User.age <= 25,
}

criterias = {
    'recommended': Rating.recommended,
    'disliked': Rating.score < 3
}


def generate(e):
    init()

    panel_name, panel = e

    for category in ['film', 'jeuvideo']:
        for critera_name, critera in criterias:
            name = panel_name + "_" + category + "_" + critera_nam

            print name

            trans_file = "results/" + name + ".trans"
            if os.path.exists(trans_file):
                with open(trans_file) as f:
                    transactions = pickle.load(f)
            else:
                transactions = filter(None, (
                    set(
                        t[0] for t in (user.rating_set
                                           .select(Rating.pid)
                                           .where(criteria)
                                           .join(Product)
                                           .where(Product.category == category)
                                           .tuples())
                    )
                    for user in User.select().where(panel)
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

from multiprocessing import Pool
pool = Pool()
pool.map(generate, panels.items())
