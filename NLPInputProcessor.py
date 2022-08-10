import gensim
import gensim.downloader
from gensim.models import Word2Vec, KeyedVectors
import nltk
from nltk.stem import WordNetLemmatizer, SnowballStemmer, PorterStemmer
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk import pos_tag
from nltk import RegexpParser
from autocorrect import Speller
import jamspell
import numpy as np
import os
import re
import string
from collections import deque
import spacy
import en_core_web_sm

spacy_model = en_core_web_sm.load()

# Uncomment to download nltk packages
# nltk.download('omw-1.4')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# nltk.download('punkt')


STOPWORDS = set(stopwords.words('english'))

FILTER = {
    "less": {"<", "less", "smaller", "below", "under", "before"},
    "greater": {">", "over", "bigger", "greater", "more", "above", "after", "higher"},
    "not": {"not"},
    "equal": {"equal", "="},
    "between": {"between"},
    "and": {"and"},
    "or": {"or"},
    }
AGGREGATORS = {
    "mean": {"mean", "average"},
    "min": {"least", "min", "minimum", "smallest", "lowest", "cheapest"},
    "max": {"max", "greatest", "most", "maximum"},
    "median": {"median"},
    "count": {"count"},
    "list": {"list", "show"},
    "stdev": {"stdev"},
    "stdevp": {"stdevp"},
    "var": {"var"},
    "varp": {"varp"},
    "group_by": {"group_by", "each", "by", "group"}
}

OPERATORS_AGGREGATORS = {}
OPERATORS_AGGREGATORS.update(FILTER)
OPERATORS_AGGREGATORS.update(AGGREGATORS)

RANGE_CHUNK = [
    'between \S* and \S*',
    'from \S* to \S*',
    'from \S* - \S*',
    'between_\S*and_\S*',
    '\S*_to_\S*',
]

AGGREGATOR_CHUNK = {
    "standard deviation": "stdev",
    "standard deviation population": "stdevp",
    "variance": "var",
    "variance population": "varp",
    "(count(?: the)(?: number of)|number of)": "count",
    "group by": "group_by"
}

GRAPH_TYPES = ["Table", "Pivot Table", "KPI Metric", "Metric Sheets", "Line Chart", "Area Chart",
               "Column Chart", "Bar Chart", "Combination Chart", "Pie Chart", "Donut Chart", "Scatter Chart"
    , "Bubble Chart", "Retention Heatmap", "Geo Map", "Point Map", "Heatmap", "Filled Map", "Conversion Funnel"
    , "Radar Chart", "Word Cloud", "Gauge Chart", "Pyramid Chart"]

UNCATEGORIZED_PHRASES = ["year old"]


class NLPInputProcessor:
    def __init__(self, raw_input: str, flattened_metadata: list):
        self.raw_input = raw_input
        self.metadata = flattened_metadata

        # detect named entities in query
        name_chunked_sentence, entities_map, names = self.named_entities(raw_input)
        self.names = names
        # preprocess user inputted query
        self.processed_input = self.preprocess(name_chunked_sentence)

        # lemmatized
        lemmatized = self.lem_sent(name_chunked_sentence)
        # spell check sentence
        spell_checked = self.spellcheck(lemmatized)

        # detect operators in inputted query
        operator_chunked_sentence, detected_operators = self.operators(spell_checked)
        self.detected_operators = detected_operators
        self.processed_input = operator_chunked_sentence

    def map_query(self):
        tokens = nltk.word_tokenize(self.processed_input)
        # chunking tokens
        chunks, chunked_tokens = self.chunking(tokens)
        # print("chunked sentence", chunked_tokens)

        # filter stopwords, number
        filtered_sentence = self.filter_sentence(tokens)

        # try literal mapping
        literal_mapped, remaining_tokens = self.literal_matching(filtered_sentence)
        mapped_literal_chunks = {key: val for key, val in chunks.items() if key in literal_mapped}

        # map remaining tokens using word2vec and wordnet
        avg_mapped = self.select_from_candidates(self.avg_map_word(remaining_tokens))
        mapped_chunks = {key: val for key, val in chunks.items() if key in avg_mapped}

        joined_tokens = " ".join(tokens)

        # group mapped chunks (correctly detected chunks)
        for key in mapped_literal_chunks.keys():
            joined_tokens = joined_tokens.replace(chunks[key], key)
        for key in mapped_chunks.keys():
            joined_tokens = joined_tokens.replace(chunks[key], key)

        all_tokens = joined_tokens.split(" ")
        # mapped items in order
        mapped_query = []
        # dictionary mapping token to mapped word and the tag
        token_to_map = dict()

        # tag the mapped query
        for token in all_tokens:
            if token == '':
                continue
            elif token in self.detected_operators:
                # mapped_query.append(self.detected_operators[token])
                # tag token
                if self.detected_operators[token] in FILTER:
                    mapped_query.append((self.detected_operators[token], "filter"))
                    token_to_map[token] = (self.detected_operators[token], "filter")
                elif self.detected_operators[token] in AGGREGATORS:
                    mapped_query.append((self.detected_operators[token], "aggregator"))
                    token_to_map[token] = (self.detected_operators[token], "aggregator")
                else:
                    mapped_query.append((self.detected_operators[token], "filter"))
                    token_to_map[token] = (self.detected_operators[token], "value")
            elif token in literal_mapped:
                # mapped_query.append(literal_mapped[token][0])
                mapped_query.append((literal_mapped[token][0], "field"))
                token_to_map[token] = (literal_mapped[token][0], "field")
            elif token in avg_mapped:
                # if token is in named entity and was mapped to a column -> keep the name + mapped column
                if avg_mapped[token][0] != '' and avg_mapped[token][0] != token:
                    # mapped_query.append(avg_mapped[token][0])
                    mapped_query.append((avg_mapped[token][0], "field"))
                    token_to_map[token] = (avg_mapped[token][0], "field")
                elif avg_mapped[token][0] != '':
                    mapped_query.append((avg_mapped[token][0], "value"))
                    token_to_map[token] = (avg_mapped[token][0], "value")

                if token in self.names and token != avg_mapped[token][0]:
                    # mapped_query.append(token)
                    mapped_query.append(("equals", "filter"))
                    mapped_query.append((token, "value"))
                    token_to_map[token] = (avg_mapped[token][0], "value")
            elif token in STOPWORDS:
                continue
            elif token.replace("_", " ") in GRAPH_TYPES:
                # mapped_query.append(token)
                mapped_query.append((token, "graph"))
                token_to_map[token] = (token, "graph")
            else:
                mapped_query.append((token, "value"))
                token_to_map[token] = (token, "value")

        return mapped_query, token_to_map

    def mapped_types(self, mapped_query):
        mapped_stuffs = {
            "dimensions": [],
            "measures": [],
            "filters": [],
            "visualization": []
        }
        fields = set(self.metadata)

        last_added = deque()
        for token, type in mapped_query:
            if token in FILTER:
                mapped_stuffs["filters"].append(token)
                last_added.append("filters")
            elif token in AGGREGATORS:
                mapped_stuffs["measures"].append(token)
                last_added.append("measures")
            elif token in fields:
                if len(last_added) > 0:
                    last_added_type = last_added.popleft()
                    mapped_stuffs[last_added_type].append(token)
                else:
                    mapped_stuffs["filters"].append(token)

                mapped_stuffs["dimensions"].append(token)
            elif token.replace("_", " ") in GRAPH_TYPES:
                mapped_stuffs["visualization"].append(token)
            else:
                # if not all 3 then it's filter value
                mapped_stuffs["filters"].append(token)
        return mapped_stuffs

    def suggestion(self):
        tokens = nltk.word_tokenize(self.processed_input)
        # chunking tokens
        chunks, chunked_tokens = self.chunking(tokens)

        last_token = tokens[-1]
        last_chunk = chunked_tokens[-1]

        literal_rec = list()
        similar_rec = list()

        literal_map, remaining = self.literal_matching([last_token])
        if len(literal_map) > 0:
            literal_rec = literal_map[last_token]

        similar_map = self.no_similarity(self.avg_map_word([last_token]))
        if len(similar_map) > 0:
            similar_rec = similar_map[last_token]

        if last_chunk != last_token:
            literal_rec_chunk, remaining = self.literal_matching([last_chunk])
            if len(literal_rec_chunk) > 0:
                literal_rec += literal_rec_chunk

            similar_rec_chunk = self.no_similarity(self.avg_map_word([last_chunk]))
            if len(similar_rec_chunk) > 0:
                similar_rec += similar_rec_chunk

        return literal_rec, similar_rec

    def spellcheck(self, sentence):
        """check spelling of words, except words that are named entities"""
        corrector = jamspell.TSpellCorrector()
        corrector.LoadLangModel('en.bin')

        sentence = nltk.word_tokenize(sentence)

        # filter out names before spell checking
        tokens = [token for token in sentence if token not in self.names]

        spell_checked = corrector.FixFragment(" ".join(tokens)).split(" ")
        spell_checked = deque(spell_checked)
        spell_checked_query = list()

        # create a list with spell checked words + named entities
        for word in sentence:
            if word not in self.names:
                spell_checked_query.append(spell_checked.popleft())
            else:
                spell_checked_query.append(word)

        joined_spell_check = " ".join(spell_checked_query)
        return joined_spell_check

    def preprocess(self, sentence):
        """remove punctuations, extra spaces"""
        sentence = sentence.strip()
        sentence = re.sub("\s+", ' ', sentence)
        punctuation = "!\"#&'()*+,-./:;?@[\]^`{|}~"
        sentence = "".join([char for char in sentence if char not in punctuation])
        return sentence

    def operators(self, sentence):
        """
            :param query: user query
            :return: map of words to its respective internal operator
        """
        operator_map = dict()
        # chunk range operator
        # chunking phrases
        for regex in RANGE_CHUNK:
            matched_phrases = re.findall(regex, sentence)
            for phrase in matched_phrases:
                replaced_phrase = "_".join(phrase.split(" "))
                sentence = sentence.replace(phrase, replaced_phrase)
                # operators_map[replaced_phrase] = "between_range"
                operator_map[replaced_phrase] = replaced_phrase

        # chunking aggregators
        for aggregator, replacement in AGGREGATOR_CHUNK.items():
            matched_phrases = re.findall(aggregator, sentence)
            for phrase in matched_phrases:
                chunked_phrase = phrase.replace(" ", "_")
                sentence = sentence.replace(phrase, chunked_phrase)
                # sentence = sentence.replace(phrase, replacement)
                # operator_map[replacement] = replacement
                operator_map[chunked_phrase] = replacement

        tokens = sentence.split(" ")
        for word in tokens:
            for key, val in OPERATORS_AGGREGATORS.items():
                # if word match operator -> add to operators mapping
                if word in val:
                    # sentence = sentence.replace(word, key)
                    # operator_map[key] = key
                    operator_map[word] = key

        return sentence, operator_map

    def named_entities(self, sentence):
        """Link to list of entities: https://stackoverflow.com/questions/59319207/ner-entity-recognition-country-filter
        :param processed_sentence - user query
        :return:
            - sentence - modified sentence (chunking named entities)
            - entity map - types of entities detected mapped to the set of words/phrases in sentence
            - names - list of names and type of name (geo location, person names, organization, etc.)"""
        processed_sentence = spacy_model(sentence)
        entity_map = dict()

        def chunk_named_entities(tags, sentence, entity_map):
            tagged_map = dict()
            for label in tags:
                if label in entity_map:
                    for tagged in entity_map[label]:
                        tagged_phrase = tagged.replace(" - ", " to ")
                        tagged_phrase = tagged_phrase.replace(" ", "_")
                        tagged_phrase = tagged_phrase.replace("$", "")
                        tagged_map[tagged_phrase] = label
                        sentence = sentence.replace(tagged, tagged_phrase)
            return sentence, tagged_map

        for ent in processed_sentence.ents:
            if ent.label_ in entity_map:
                entity_map[ent.label_].add(ent.text)
            else:
                entity_map[ent.label_] = {ent.text}

        names_tags = ["PERSON", "LOC", "ORG", "FAC", "GPE", "WORK_OF_ART", "LANGUAGE"]
        sentence, name_map = chunk_named_entities(names_tags, sentence, entity_map)

        # tag graph types detected as GRAPH
        for graph in GRAPH_TYPES:
            if re.search(graph, sentence, flags=re.IGNORECASE):
                name_phrase = graph.replace(" ", "_")
                sentence = re.sub(graph, name_phrase, sentence, flags=re.IGNORECASE)
                name_map[name_phrase] = "GRAPH"

        amount_tag = ["PERCENT", "QUANTITY", "MONEY"]
        sentence, amount_map = chunk_named_entities(amount_tag, sentence, entity_map)
        return sentence, entity_map, name_map

    # lemmatization - WordNetLemmatizer
    def lem_sent(self, sentence):
        """Lemmatize sentence to convert to its base form, except words that are named entities"""
        lemmatized = list()
        lemmatizer = WordNetLemmatizer()
        for word in nltk.word_tokenize(sentence):
            if word not in self.names:
                word = lemmatizer.lemmatize(word.lower())
                lemmatized.append(word)
            else:
                lemmatized.append(word)
        return " ".join(lemmatized)

    def get_word2vec(self):
        """Get word2vec model"""
        model = None
        if not os.path.isfile("./word2vec.model"):
            model = gensim.downloader.load('fasttext-wiki-news-subwords-300')
            # model = gensim.downloader.load('word2vec-google-news-300')
            # model = gensim.downloader.load('conceptnet-numberbatch-17-06-300')
            model.save("word2vec.model")
        else:
            model = KeyedVectors.load("word2vec.model")
        return model

    def pos_tagging(self, tokens):
        """Part-of-speech tagging for each token, tag notations:
            https://www.learntek.org/blog/categorizing-pos-tagging-nltk-python/
            return tagged list and chunked list
        """
        token_tag = pos_tag(tokens)
        token_tag_map = dict()
        for word, pos in token_tag:
            token_tag_map[word] = pos
        return token_tag_map

    def chunking(self, tokens):
        """get compound nouns from pos tagged words
            defined structure of compound nouns is group of Nouns"""
        # list storing words and compound words detected
        chunks = dict()

        # filter out operator words, replace with a random filler word (by) to avoid chunking 2 consecutive nouns
        tokens = [token if token not in self.detected_operators else "by" for token in tokens]
        # filter out name chunk, replace with a random filler word (by) to avoid chunking 2 consecutive nouns
        chunking_tokens = [token if token not in self.names else "by" for token in tokens]

        token_tag = pos_tag(chunking_tokens)
        # pattern = "NP:{<JJ>?<NN|NNP|NNS|NNPS>+<JJ>?}"
        pattern = "NP:{<NN|NNP|NNS|NNPS>+}"

        regex_parser = RegexpParser(pattern)
        compound = regex_parser.parse(token_tag)

        # iterate each branch of a tree
        for branch in compound:
            # if branch is another subtree -> it is a compound nouns
            if type(branch) == nltk.Tree:
                words = [token for token, pos in branch.leaves()]
                phrase = " ".join(words)
                chunks["_".join(words)] = phrase

        # replace all the detected phrases with chunk
        joined_tokens = " ".join(tokens)
        for chunk, phrase in chunks.items():
            joined_tokens = joined_tokens.replace(phrase, chunk)

        # chunking special phrases
        for phrase in UNCATEGORIZED_PHRASES:
            if phrase in joined_tokens:
                replaced_phrase = phrase.replace(" ", "_")
                joined_tokens = joined_tokens.replace(phrase, replaced_phrase)
                chunks[replaced_phrase] = phrase

        chunked_tokens = joined_tokens.split(" ")

        return chunks, chunked_tokens

    def filter_sentence(self, tokens):
        """Filter stopwords, comparisons from tokens of sentence"""
        # set of english stopwords
        # stop_words = set(stopwords.words('english'))
        # get list of token and its tags
        token_tag_map = self.pos_tagging(tokens)
        filtered_sentence = []

        # filter out operator words and numeric values
        for word in tokens:
            if word in STOPWORDS:
                continue
            if token_tag_map[word] == "CD":
                continue
            if word in self.detected_operators:
                continue
            else:
                filtered_sentence.append(word)

        return filtered_sentence

    def literal_matching(self, tokens):
        """
        :param tokens: tokens of user's query
        Helper function: literal_map_word
        :return: map each token to list of keywords (if token is all or part of keywords), list of remaining tokens
        """

        def literal_map_word(curr_word, metadata):
            if curr_word in metadata:
                # extract exact map (token/ word in query exactly the same as keywords)
                return curr_word
            else:
                # check if token in query match a part of keywords (fuzzy matching)
                for word in internal_keywords:
                    if word.find(curr_word) != -1:  # check if token is a substring of an internal keyword
                        return word
            return None

        literal_map = dict()
        internal_keywords = set(self.metadata)
        unmapped = []

        for token in tokens:
            mapped = literal_map_word(token, internal_keywords)
            # try mapping token to keywords
            if mapped is not None:
                # add mapped keyword to list
                if token in literal_map:
                    literal_map[token].append(mapped)
                else:
                    literal_map[token] = [mapped]
                # remove token in list of tokens to avoid repetitive process
                if token in tokens:
                    tokens.remove(token)

            elif '_' in token:
                # if token is a chunk and not able to map -> map by individual token
                for chunk_token in token.split("_"):
                    chunk_mapped = literal_map_word(chunk_token, internal_keywords)
                    if chunk_mapped is not None:
                        if chunk_token in literal_map:
                            literal_map[chunk_token].append(chunk_mapped)
                        else:
                            literal_map[chunk_token] = [chunk_mapped]
                        if token in tokens:
                            # remove token in list of tokens being mapped to avoid repetitive process
                            tokens.remove(token)
                    else:
                        # unable to map literally
                        unmapped.append(chunk_token)
        tokens = tokens + unmapped
        return literal_map, tokens

    def avg_map_word(self, words):
        """
        :param words: list of filtered words in query
        :return: dictionary mapping each word to list of candidates mapping keywords (similarity>0.25) from metadata
                in the format {"word":[(candidate, similarity), ...], ...}
        """

        model = self.get_word2vec()
        avg_map = dict()

        def map_word(curr_word, internal_keywords):
            candidates_map = list()
            if "_" in curr_word:
                # if the word is a chunk, preprocess the chunk before mapping
                curr_word = curr_word.replace("_", "")

            if curr_word in self.names:
                # if curr word is a named entity, only map if it is a location (provide implicit reference for location)
                if self.names[curr_word] != "LOC" and self.names[curr_word] != "GPE":
                    # if word is not a location, map to itself
                    return [(curr_word, 1)]

            mapped = None
            highest_similarity = 0
            # map to internal word
            for keyword in internal_keywords:
                # try mapping by word2vec
                try:
                    vec_simi = model.similarity(curr_word, keyword)
                except:
                    vec_simi = 0

                # try mapping by wordnet
                try:
                    keyword_synset = wn.synsets(keyword)[0]
                    word_synset = wn.synsets(curr_word)[0]
                    net_simi = wn.path_similarity(keyword_synset, word_synset)
                except:
                    net_simi = 0

                # if one of the similarity is 0, takes the value of the other one as average value
                if net_simi == 0:
                    avg_simi = vec_simi
                elif vec_simi == 0:
                    avg_simi = net_simi
                else:
                    similarity_measurement_list = np.array([vec_simi, net_simi])
                    avg_simi = np.average(similarity_measurement_list)
                # if the current keyword have the highest similarity -> update the mapped keyword
                # if avg_simi > highest_similarity:
                #     highest_similarity = avg_simi
                #     mapped = keyword

                if avg_simi > 0.25:
                    candidates_map.append((keyword, avg_simi))

            # benchmark: only map if similarity is higher than 0.25
            # if highest_similarity < 0.25:
            #     mapped, highest_similarity = None, 0
            return candidates_map

        for word in words:
            mapped_candidates = map_word(word, self.metadata)

            if len(mapped_candidates) > 0:
                avg_map[word] = mapped_candidates
            else:
                # if the word is a chunk and unable to map -> map by individual words
                if '_' in word:
                    for chunk_word in word.split("_"):
                        chunk_mapped = map_word(chunk_word, self.metadata)
                        if len(chunk_mapped) > 0:
                            if chunk_word in avg_map:
                                avg_map[chunk_word] = avg_map[chunk_word] + chunk_mapped
                            else:
                                avg_map[chunk_word] = []
                        else:
                            if chunk_word not in avg_map:
                                avg_map[chunk_word] = []
                else:
                    avg_map[word] = []
        return avg_map

    def select_from_candidates(self, map_word_candidates):
        """
        :param map_word: dictionary mapping word to list of mapping candidates (from avg_map_word method)
        :return: dictionary mapping word to keyword (from metadata) with highest similarity
        """
        map_word_keyword = dict()
        for word, candidates in map_word_candidates.items():
            if len(candidates) > 0:
                most_similar = max(candidates, key=lambda x: x[1])
                map_word_keyword[word] = most_similar
            else:
                map_word_keyword[word] = ('', 0)

        return map_word_keyword

    def no_similarity(self, map_word_candidates):
        """
        :param map_word_candidates: dictionary mapping word to list of mapping candidates (from avg_map_word method)
        :return: dictionary mapping word to list of mapping candidates without similarity
        """

        map_word_keyword = dict()
        for word, candidates in map_word_candidates.items():
            candidate_list = list()
            for candidate_word, similarity in candidates:
                candidate_list.append(candidate_word)

            map_word_keyword[word] = candidate_list

        return map_word_keyword


def main():
    query = ["Average spending of customers in Hanoi, Vietnam",
             "Average spending of customers before last November",
             "Most profit from animation company that is not Disney from 2012 to 2020",
             "Most profit from animation company with gross profit from $20 million - $50 million",
             "Movies that have higher profit than Frozen, Moana and Beauty and the Beast",
             "standard deviations of sale last quarter",
             "show geo map of customers by country",
             "numbers of patients who is from New York and over 50 years old"]

    sample = ['sale', 'country', 'client', 'age', 'production_company', 'date', 'city', "movie"]

    for sentence in query:
        nlp_processor = NLPInputProcessor(sentence, sample)
        mapped_query, token_to_tag = nlp_processor.map_query()
        mapped_types = nlp_processor.mapped_types(mapped_query)

        print("Sentence: ", sentence)
        print(">> Mapped query: ", mapped_query)
        print(">> Mapped with tags: ", token_to_tag)
        print(">> Mapped types: ", mapped_types)
        print()

    # sample_suggestion = ["Aver",
    #          "Most profit from animation company",
    #          "Most profit from animatio",
    #          "Movi",
    #          "Most pro",
    #          "show geo map of customers by country"]
    #
    # for sentence in sample_suggestion:
    #     nlp_processor = NLPInputProcessor(sentence, sample)
    #     mapped_query = nlp_processor.suggestion()
    #
    #     print("Sentence: ", sentence)
    #     print(">> Suggestion ", mapped_query)

if __name__ == "__main__":
    main()
