import os
import cPickle as pickle
import json

from itertools import chain, count, combinations
from collections import Counter

from .db import User, Rating, Product, init

init()

minsup = 0.33
minconf = 0.8

if os.path.exists('transactions'):
    with open('transactions') as f:
        transactions = pickle.load(f)
else:
    transactions = filter(None, (
        frozenset(t[0] for t in user.rating_set.select(Rating.pid).join(Product).where(Rating.recommended and Product.category == 'film').tuples())
        for user in User.select()
    ))

    with open('transactions', 'w+') as f:
        pickle.dump(transactions, f, pickle.HIGHEST_PROTOCOL)

if os.path.exists('associations'):
    with open('associations') as f:
        result = pickle.load(f)
else:
    counter = Counter(chain(*transactions))
    minfreq = minsup * len(transactions)
    print minfreq
    l1 = set(item for item, freq in counter.items() if freq >= minfreq)
    print 1, len(l1)

    print "before", len(transactions)
    transactions = filter(lambda t: len(t) >= 2, (t & l1 for t in transactions))
    print "after", len(transactions)

    result = {frozenset((item,)): counter[item] for item in l1}
    prev_l = result.keys()

    for k in count(2):
        print "candidates"
        candidates = (frozenset(e) for e in (a | b for a in prev_l for b in prev_l) if len(e) == k)
        candidates = (c for c in set(candidates) if all(set(subset) in prev_l for subset in combinations(c, k - 1)))
        print "done"

        l = set()
        for c in candidates:
            freq = sum(1 for t in transactions if c <= t)
            if freq >= minfreq:
                l.add(c)
                result[c] = freq

        print k, len(l)

        if not l:
            break

        prev_l = l

    with open('associations', 'w+') as f:
        pickle.dump(result, f, pickle.HIGHEST_PROTOCOL)

rules = list()
for items, freq in result.items():
    if len(items) < 2:
        continue

    candidates = (frozenset(r) for k in range(1, len(items)) for r in combinations(items, k))
    confidant = set((items - r, r) for r in candidates if float(freq) / result[items - r] >= minconf)

    if not confidant:
        break

    rules += confidant

print len(rules)

output = []
nb_transactions = float(len(transactions))
for l, r in rules:
    conf = float(result[l | r]) / result[l]
    lift = conf * (nb_transactions / result[r])
    leverage = (result[l | r] / nb_transactions) - (result[l] / nb_transactions) * (result[r] / nb_transactions)

    l, r = ([Product.get(Product.pid == pid).name for pid in items] for items in (l, r))

    output.append({'l': l, 'r': r, 'conf': conf, 'lift': lift, 'leverage': leverage})

with open("toto.json", 'w+') as f:
    json.dump(output, f, indent=2)
