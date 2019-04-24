from collections import defaultdict
import itertools


class RelativeSupportApriori:

    def __init__(self, data, min_sup, max_sup, r_sup, min_conf):
        self.data = data
        self.min_sup = min_sup
        self.max_sup = max_sup
        self.min_r_sup = r_sup
        self.min_conf = min_conf

        self.freq_dict = defaultdict(int)
        self.F1 = set()  # F==L,
        self.R1 = set()  # R==NL
        self.rule_input = defaultdict(int)

    def get_candidate_itemsets(self):
        for trans in self.data:
            for item in trans:
                self.freq_dict[tuple([item])] += 1
                self.rule_input[frozenset({item})] += 1

        self.F1 = set([item for item, support in self.freq_dict.items() if support >= self.max_sup])
        self.R1 = set([item for item, support in self.freq_dict.items() if self.max_sup > support >= self.min_sup])

        NC2 = self.rsaa_gen(self.R1, 2)  # NC2
        NLC2 = self.rsaa_gen2(self.R1, self.F1, 2)  # NL2

        NL = self.gen_quasi(NC2)
        NLL = self.gen_quasi(NLC2)

        k = 3
        while len(NL) != 0 or len(NLL) != 0:
            NC = self.rsaa_gen(NL, k)
            NLC = self.rsaa_gen(NLL, k)
            NL = self.gen_quasi(NC)
            NLL = self.gen_quasi(NLC)
            k += 1

        return self.rule_input

    def rsaa_gen(self, itemsets, k):
        if k == 2:
            candidate = [tuple(sorted([x[0], y[0]])) for x in itemsets for y in itemsets if
                         len((x[0], y[0])) == k and x[0] != y[0]]
        else:
            candidate = list(itertools.combinations(itemsets, 2))
            candidate = [set(i[0]).union(i[1]) for i in candidate]
            candidate = [tuple(sorted(i)) for i in candidate if len(i) == k]

        candidate = list(set(candidate))
        for idx in range(len(candidate)-1, -1, -1):
            subsets = self.gen_subsets(candidate[idx], k - 1)
            if any([x not in itemsets for x in subsets]):
                candidate.pop(idx)
        return set(candidate)

    def rsaa_gen2(self, itemset1, itemset2, k):
        candidate = [tuple(sorted(set(x).union(y))) for x in itemset1 for y in itemset2 if set(x) != set(y)]
        candidate = [x for x in candidate if len(x) == k]
        return set(candidate)

    def gen_quasi(self, candidate):  # NC or NLC
        ret = set()
        cands_temp = set()
        for trans in self.data:
            for cand in candidate:
                if len(cand) > len(trans):
                    continue
                if set(cand).issubset(trans):
                    self.freq_dict[cand] += 1
                    cands_temp.add(cand)
        for cand in cands_temp:
            if self.freq_dict[cand] >= self.min_sup:
                r_sup_b = min([self.freq_dict[(item,)] for item in cand])
                count = self.freq_dict[cand]
                r_sup = count / r_sup_b
                if r_sup >= self.min_r_sup:
                    ret.add(cand)
                    self.rule_input[frozenset(cand)] = count
        return ret

    def gen_subsets(self, items, m):
        subsets = []
        subsets.extend(itertools.combinations(items, m))
        return subsets


if __name__ == '__main__':
    data = [(1, 2, 3), (3, 4), (1, 2, 3, 4, 5, 6, 7), (6, 7), (3, 4, 5, 6), (1, 2), (3, 4, 6, 7), (1, 2),
            (1, 3, 4, 5, 6), (1, 2)]
    rsaa = RelativeSupportApriori(data, 2, 4, 0.7, 0)
    print(rsaa.get_candidate_itemsets())
