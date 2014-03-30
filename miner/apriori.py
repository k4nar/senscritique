import os
import cPickle as pickle

from multiprocessing import Pool
from itertools import chain, count, combinations
from collections import Counter

from .db import User, Rating, Product, init

init()

minsup = 0.03

if os.path.exists('transactions'):
    with open('transactions') as f:
        transactions = pickle.load(f)
else:
    transactions = filter(None, (
        frozenset(t[0] for t in user.rating_set.select(Rating.pid).where(Rating.recommended).tuples())
        for user in User.select().limit(1000)
    ))

    with open('transactions', 'w+') as f:
        pickle.dump(transactions, f, pickle.HIGHEST_PROTOCOL)

if os.path.exists('associations'):
    with open('associations') as f:
        result = pickle.load(f)
else:
    support = Counter(chain(*transactions))
    minfreq = minsup * len(transactions)
    print minfreq
    print support.most_common(1)
    l1 = set(item for item, freq in support.items() if freq >= minfreq)
    print 1, len(l1)

    print "before", len(transactions)
    transactions = filter(lambda t: len(t) >= 2, (t & l1 for t in transactions))
    print "after", len(transactions)

    prev_l = set(frozenset((item,)) for item in l1)
    result = {}

    for k in count(2):
        candidates = (frozenset(e) for e in (a | b for a in prev_l for b in prev_l) if len(e) == k)
        candidates = (c for c in set(candidates) if all(set(subset) in prev_l for subset in combinations(c, k - 1)))

        pool = Pool()
        l = set(pool.map(lambda c: c if sum(c <= t for t in transactions) >= minfreq else None, candidates))
        l.discard(None)

        print k, len(l)

        if not l:
            break

        result[k] = l
        prev_l = l

    with open('associations', 'w+') as f:
        pickle.dump(result, f, pickle.HIGHEST_PROTOCOL)

from pprint import pprint
pprint(result)
