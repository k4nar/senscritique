import os
import cPickle as pickle

from itertools import chain, count, combinations
from collections import Counter


def apriori(transactions, minsup, minconf, freq_file=None):
    """
    Run the Apriori algorithm with the given transactions.
    The transactions must be a list of sets of items.

    Returns the rules as a dictionary.
    """

    # Compute the number of transactions in order to calculate the support
    nb_transactions = float(len(transactions))

    # We get the frequent itemsets from if they were persisted
    if freq_file and os.path.exists(freq_file):
        with open(freq_file) as f:
            frequencies = pickle.load(f)
    else:
        # Count each item in the transactions
        counter = Counter(chain(*transactions))
        # Get the supported items
        l1 = set(item for item, freq in counter.items() if freq / nb_transactions >= minsup)

        # We delete all the items in the transactions that are not supported,
        # as they are now useless for the following calculations
        transactions = [t & l1 for t in transactions]

        # We start constructing the dictionary containing the frequent itemsets
        # with the first iteration
        frequencies = {frozenset((item,)): counter[item] for item in l1}

        # We store the previous itemsets at each iteration in order to compute
        # the candidates
        prev_l = frequencies.keys()

        for k in count(2):
            # We filter the transactions of cardinality lesser than k
            transactions = filter(lambda t: len(t) >= k, transactions)

            # We compute the candidates using the previous itemsets.
            # This is a generator, each value will be calculated when needed
            candidates = (frozenset(e) for e in (a | b for a in prev_l for b in prev_l) if len(e) == k)
            candidates = (
                c for c in set(candidates)
                if all(set(subset) in prev_l for subset in combinations(c, k - 1))
            )

            # We filter the candidates in order to get the supported itemsets
            l = set()
            for c in candidates:
                # frequency of the candidate
                freq = sum(1 for t in transactions if c <= t)

                if freq / nb_transactions >= minsup:
                    l.add(c)
                    frequencies[c] = freq

            # If we didn't found any supported itemsets, we stop
            if not l:
                break

            prev_l = l

        # We persist the frequent itemsets in a file if provided
        if freq_file:
            with open(freq_file, 'w+') as f:
                pickle.dump(frequencies, f, pickle.HIGHEST_PROTOCOL)

    # We can now generate the rules
    rules = {}
    for items, freq in frequencies.items():
        if len(items) < 2:
            continue

        # the support of the current itemset
        support = frequencies[items] / nb_transactions

        # We compute all the possible candidates
        candidates = (frozenset(r) for k in range(1, len(items)) for r in combinations(items, k))

        # We filter the candidates using minconf
        for r in candidates:
            l = items - r
            conf = float(freq) / frequencies[l]

            if conf >= minconf:
                lift = conf * (nb_transactions / frequencies[r])
                leverage = support - (frequencies[l] * frequencies[r]) / (nb_transactions ** 2)

                rules[(l, r)] = (conf, lift, leverage)

    return rules
