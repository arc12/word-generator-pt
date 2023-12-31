# read from a file input text, where each line is taken separately and digested to create a set of probabilities for the letter which follows
# a given substring. "Given substrings" include "start" and the following letter includes "end".
# From these, new utterances are generated.
# The input file may contain sensible punctuation, but not $ or ^ symbols. Any kind of bracket should be avoided (because these end up being un-matched).

from collections import defaultdict
import pickle
from random import choices

class WordGenerator:
    def __init__(self, seed_words_file, substring_length):
        self.substring_length = substring_length  # number of letters to compute probabilities for following letter
        self.start_pattern = "$" * substring_length  # this is the "start" signal
        occurrences_ = defaultdict(lambda: defaultdict(int))
        
        with open(seed_words_file, 'r', encoding="utf-8") as f:
            for line in f:
                current_set = self.start_pattern
                line = f.readline().strip().lower().replace("$", "").replace("^", "").replace("(", "").replace(")", "").replace("[", "").replace("]", "")
                if len(line) < self.substring_length:
                    continue
                for char in line:
                    occurrences_[current_set][char] += 1
                    # occurrences_[current_set]["sum"] += 1
                    current_set = current_set[1:] + char
                occurrences_[current_set]["^"] += 1  # this is the "end" signal
                # occurrences_[current_set]["sum"] += 1

        # collapse the accumulator dictionaries into lists of characters and their weights
        self.occurrences = {k: {"letters": list(v.keys()), "weights": list(v.values())} for k, v in occurrences_.items()}

    def save_pickle(self, pickle_file):
        with open(pickle_file, 'wb') as f:
            pickle.dump(self, f)

    def _get_current_set(self, prior):
        current_set = prior[-self.substring_length:].lower()
        if len(current_set) < self.substring_length:
            current_set = "$" * max(0, self.substring_length - len(current_set)) + current_set
        return current_set
    
    def generate_character(self, prior, append=True):
        # prior is the string "so far"; this method returns a randomised next character or None if there are no learned occurrences of the ending substring
        # trailing space characters are permitted (only one) but initial space chars are removed.
        # This MAY return "^" as the new character, signalling the end of the word.
        
        prior = prior.lstrip()
        current_set = self._get_current_set(prior)

        if current_set not in self.occurrences:
            return None  # this should never happen for complete word generation; only possible for user-entered "prior"

        focus = self.occurrences[current_set]
        new_char = choices(focus["letters"], weights=focus["weights"], k=1)[0]

        return prior + new_char if append else new_char

    def generate_start(self):
        # generates the start of a word, returning a string of length = substring_length
        word = ""
        for i in range(self.substring_length):
            word = self.generate_character(word)
        return word

    def generate_word(self):
        # generates a complete word, i.e. until the "end" placeholder is chosen (although this is NOT returned)
        word = ""
        while True:
            word = self.generate_character(word)
            if word[-1] == "^":
                break
        return word[:-1]

    def get_options(self, prior, round_to=1):
        # gets the possible next characters after prior and their normalised weights (as %), or None if no options for prior
        prior = prior.lstrip()
        current_set = self._get_current_set(prior)
        
        if current_set not in self.occurrences:
            return None
        
        focus = self.occurrences[current_set]
        norm_factor = sum(focus["weights"])
        return {letter: round(100 * weight / norm_factor, round_to) for letter, weight in zip(focus["letters"], focus["weights"])}