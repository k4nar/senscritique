import os
import json
import cPickle as pickle

from .db import User, Rating, Product, init
from .apriori import apriori

minsup = 0.1
minconf = 0.8

# The panels of users we want to use
panels = {
    "all": None,
    "men": User.gender == 'm',
    "women": User.gender == 'f',
    "oldest": User.age > 25,
    "youngest": User.age <= 25,
}

# The different criterias used to split the ratings
criterias = {
    'recommended': Rating.recommended,
    'disliked': Rating.score < 3
}

# The categories used to split the products
categories = ['film', 'jeuvideo']


def generate(panel):
    init()

    panel_name, panel = panel

    for category in categories:
        for critera_name, criteria in criterias.items():
            name = panel_name + "_" + category + "_" + critera_name

            # We get the transactions
            # the transactions are persisted in order to be able to launch
            # the algorithm a second time without hitting the database
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

            # We get the rules from the apriori function
            rules = apriori(transactions, minsup, minconf, "results/" + name + ".freq")

            # We export the rules in json
            with open("results/" + name + ".json", 'w+') as f:
                rules_export = []
                for rule, (conf, lift, leverage) in rules.items():
                    l, r = ([Product.get(Product.pid == pid).name for pid in items] for items in rule)
                    rules_export.append({'l': l, 'r': r, 'conf': conf, 'lift': lift, 'leverage': leverage})

                output = {
                    'minconf': minconf,
                    'minsup': minsup,
                    'rules': rules_export
                }

                json.dump(output, f, indent=2)


if __name__ == '__main__':
    # We launch the generation in separate processes
    from multiprocessing import Pool
    pool = Pool()
    pool.map(generate, panels.items())
