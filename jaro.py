from textdistance.algorithms.base import BaseSimilarity

class JaroWinkler(BaseSimilarity):
    """
    Computes the Jaro-Winkler measure between two strings.
    The Jaro-Winkler measure is designed to capture cases where two strings
    have a low Jaro score, but share a prefix.
    and thus are likely to match.

    https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance
    https://github.com/Yomguithereal/talisman/blob/master/src/metrics/distance/jaro.js
    https://github.com/Yomguithereal/talisman/blob/master/src/metrics/distance/jaro-winkler.js
    """
    def __init__(self, long_tolerance=False, winklerize=True, qval=1, external=True):
        self.qval = qval
        self.long_tolerance = long_tolerance
        self.winklerize = winklerize
        self.external = external

    def maximum(self, *sequences):
        return 1

    def __call__(self, s1, s2, lenquery, prefix_weight=0.1):
        # s1, s2 = self._get_sequences(s1, s2)

        # result = self.quick_answer(s1, s2)
        # if result is not None:
        #     return result

        s1_len = len(s1)
        s2_len = len(s2)

        if not s1_len or not s2_len:
            return 0.0

        min_len = max(s1_len, s2_len)
        search_range = (min_len // 2) - 1
        if search_range < 0:
            search_range = 0

        s1_flags = [False] * s1_len
        s2_flags = [False] * s2_len

        # looking only within search range, count & flag matched pairs
        common_chars = 0
        for i, s1_ch in enumerate(s1):
            low = max(0, i - search_range)
            hi = min(i + search_range, s2_len - 1)
            for j in range(low, hi + 1):
                if not s2_flags[j] and s2[j] == s1_ch:
                    s1_flags[i] = s2_flags[j] = True
                    common_chars += 1
                    break

        # short circuit if no characters match
        if not common_chars:
            return 0.0

        # count transpositions
        k = trans_count = 0
        for i, s1_f in enumerate(s1_flags):
            if s1_f:
                for j in range(k, s2_len):
                    if s2_flags[j]:
                        k = j + 1
                        break
                if s1[i] != s2[j]:
                    trans_count += 1
        trans_count //= 2

        # adjust for similarities in nonmatched characters
        weight = common_chars / s1_len + common_chars / s2_len
        weight += (common_chars - trans_count) / common_chars
        weight /= 3

        # stop to boost if strings are not similar
        if not self.winklerize:
            return weight
        if weight <= 0.7 or s1_len <= 3 or s2_len <= 3:
            return weight

        # winkler modification
        # adjust for up to first 4 chars in common
        j = min(min_len, 4)
        i = 0
        while i < j and s1[i] == s2[i] and s1[i]:
            i += 1
        if i:
            weight += i * prefix_weight * (1.0 - weight)

        # optionally adjust for long strings
        # after agreeing beginning chars, at least two or more must agree and
        # agreed characters must be > half of remaining characters
        if not self.long_tolerance or min_len <= 4:
            return weight
        if common_chars <= i + 1 or 2 * common_chars < min_len + i:
            return weight
        tmp = (common_chars - i - 1) / (lenquery + s2_len - i * 2 + 2)
        weight += (1.0 - weight) * tmp
        return weight


jaroWinkler = JaroWinkler()
