import os
import cPickle as pickle

from itertools import chain, count, combinations
from collections import Counter

from .db import User, Rating, Product, init

init()

minsup = 0.01

if os.path.exists('transactions'):
    with open('transactions') as f:
        transactions = pickle.load(f)
else:
    transactions = filter(None, (
        frozenset(t[0] for t in user.rating_set.select(Rating.pid).where(Rating.recommended == True).tuples())
        for user in User.select()
    ))

    with open('transactions', 'w+') as f:
        pickle.dump(transactions, f, pickle.HIGHEST_PROTOCOL)


support = Counter(chain(*transactions))
minfreq = minsup * len(transactions)
print minfreq
print support.most_common(1)
l1 = set(item for item, freq in support.items() if freq >= minfreq)
print len(l1)

print "before", len(transactions)
for t in transactions:
    if len(t & l1) < 2:
        transactions.remove(t)
print "after", len(transactions)

prev_l = set(frozenset((item,)) for item in l1)
result = prev_l

for k in count(2):
    candidates = set(frozenset(e) for e in (a | b for a in prev_l for b in prev_l) if len(e) == k)
    print "a", len(candidates)
    candidates = set(c for c in candidates if all(set(subset) in prev_l for subset in combinations(c, k - 1)))
    print "b", len(candidates)

    from multiprocessing import Pool
    pool = Pool()
    l = set(pool.map(lambda c: c if sum(c <= t for t in transactions) >= minfreq else None, candidates))
    l.discard(None)

    print "c", len(l)

    if not l:
        break

    result |= l
    prev_l = l

print result
