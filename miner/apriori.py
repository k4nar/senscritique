import os
import json
import cPickle as pickle

from itertools import chain, count, combinations
from collections import Counter


def apriori(transactions, minsup, minconf, freq_file=None):
    nb_transactions = float(len(transactions))

    if freq_file and os.path.exists(freq_file):
        with open(freq_file) as f:
            frequencies = pickle.load(f)
    else:
        counter = Counter(chain(*transactions))
        l1 = set(item for item, freq in counter.items() if freq / nb_transactions >= minsup)

        transactions = [t & l1 for t in transactions]

        frequencies = {frozenset((item,)): counter[item] for item in l1}
        prev_l = frequencies.keys()

        for k in count(2):
            transactions = filter(lambda t: len(t) >= k, transactions)

            candidates = (frozenset(e) for e in (a | b for a in prev_l for b in prev_l) if len(e) == k)
            candidates = (c for c in set(candidates) if all(set(subset) in prev_l for subset in combinations(c, k - 1)))

            l = set()
            for c in candidates:
                freq = sum(1 for t in transactions if c <= t)
                if freq / nb_transactions >= minsup:
                    l.add(c)
                    frequencies[c] = freq

            if not l:
                break

            prev_l = l

        if freq_file:
            with open(freq_file, 'w+') as f:
                pickle.dump(frequencies, f, pickle.HIGHEST_PROTOCOL)

    rules = {}
    for items, freq in frequencies.items():
        if len(items) < 2:
            continue

        support = frequencies[items] / nb_transactions
        candidates = set(frozenset(r) for k in range(1, len(items)) for r in combinations(items, k))

        for r in candidates:
            l = items - r
            conf = float(freq) / frequencies[l]
            if conf >= minconf:
                lift = conf * (nb_transactions / frequencies[r])
                leverage = support - (frequencies[l] * frequencies[r]) / (nb_transactions ** 2)
                rules[(l, r)] = (conf, lift, leverage)

    return rules
