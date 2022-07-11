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

# define root path to current directory
root = os.getcwd()


def preprocess(sentence):
    """remove punctuations, extra spaces"""
    sentence = sentence.strip()
    sentence = re.sub("\s+", ' ', sentence)
    punctuation = "!\"#&'()*+,-./:;?@[\]^`{|}~"
    sentence = "".join([char for char in sentence if char not in punctuation])
    return sentence


# stemming - Snowball stemmer
def stem_sent(sentence):
    """Stem sentence to convert to its base form"""

    sentence = sentence.lower()
    # stemmer = SnowballStemmer("english")
    stemmer = PorterStemmer()
    stemmed = [stemmer.stem(word) for word in nltk.word_tokenize(sentence)]
    return " ".join(stemmed)


# lemmatization - WordNetLemmatizer
def lem_sent(sentence, name_chunks):
    """Lemmatize sentence to convert to its base form, except words that are named entities"""
    lemmatized = list()
    lemmatizer = WordNetLemmatizer()
    for word in nltk.word_tokenize(sentence):
        if word not in name_chunks:
            word = lemmatizer.lemmatize(word.lower())
            lemmatized.append(word)
        else:
            lemmatized.append(word)
    return " ".join(lemmatized)


def spellcheck(sentence, name_chunks):
    """check spelling of words, except words that are named entities"""
    corrector = jamspell.TSpellCorrector()
    corrector.LoadLangModel('en.bin')

    sentence = nltk.word_tokenize(sentence)

    # filter out names before spell checking
    tokens = [token for token in sentence if token not in name_chunks]

    spell_checked = corrector.FixFragment(" ".join(tokens))

    return spell_checked.split(" ")


def get_word2vec():
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


def avg_map_word(words, internal_keywords, name_list):
    model = get_word2vec()
    avg_map = dict()

    def map_word(curr_word):
        if "_" in curr_word:
            # if the word is a chunk, preprocess the chunk before mapping
            curr_word = curr_word.replace("_", "")

        if curr_word in name_list:
            # if curr word is a named entity, only map if it is a location (provide implicit reference for location)
            if name_list[curr_word] != "LOC" and name_list[curr_word] != "GPE":
                # if word is not a location, map to itself
                return curr_word, 1

        mapped = None
        highest_similarity = 0
        # map to internal word
        for keyword in internal_keywords:
            try:
                vec_simi = model.similarity(curr_word, keyword)
            except:
                vec_simi = 0
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
            if avg_simi > highest_similarity:
                highest_similarity = avg_simi
                mapped = keyword

        # benchmark: only map if similarity is higher than 0.11
        if highest_similarity < 0.11:
            mapped, highest_similarity = None, 0
        return mapped, highest_similarity

    for word in words:
        mapped_keyword, similarity = map_word(word)
        if mapped_keyword is not None:
            avg_map[word] = (mapped_keyword, similarity)
        else:
            # if the word is a chunk and unable to map -> map by individual words
            if '_' in word:
                for chunk_word in word.split("_"):
                    chunk_mapped, chunk_similarity = map_word(chunk_word)
                    if chunk_mapped is not None:
                        avg_map[chunk_word] = (chunk_mapped, chunk_similarity)
                    else:
                        avg_map[chunk_word] = ('', 0)
            else:
                avg_map[word] = ('', 0)

    return avg_map


def mapped_operators(tokens):
    """
    :param tokens: list of tokens in tokenized query
    :return: map of words to its respective internal operator
    """

    miscellaneous_operators = {
        "less": {"<", "less", "smaller", "below", "under", "before"},
        "greater": {">", "over", "bigger", "greater", "more", "above", "after", "higher"},
        "not": {"not"},
        "equal": {"equal", "="},
        "between": {"between"},
        "and": {"and"},
        "or": {"or"},
        "mean": {"mean", "average"},
        "group_by": {"each", "by", "group"},
        "min": {"least", "min", "minimum", "smallest", "lowest", "cheapest"},
        "max": {"max", "greatest", "most", "maximum"},
        "median": {"median"},
        "count": {"count"},
        "list": {"list", "show"}
    }

    aggregator = ["count", "average", "min", "max", "sum", "median", "list"]

    # list of operators that can be mapped using word2vec and wordnet
    flexible_operators = ["average", "count", "sum", "min", "max"]

    operators_map = dict()

    joined_token = " ".join(tokens)

    # chunk range operator
    range_operator_chunk = [
        'between \S* and \S*',
        'from \S* to \S*',
        'from \S* - \S*'
    ]
    for regex in range_operator_chunk:
        matched_phrases = re.findall(regex, joined_token)
        for phrase in matched_phrases:
            replaced_phrase = "_".join(phrase.split(" "))
            joined_token = joined_token.replace(phrase, replaced_phrase)
            operators_map[replaced_phrase] = "between"

    aggregator_chunk = {
        "standard deviation": "stdev",
        "standard deviation population": "stdevp",
        "variance": "var",
        "variance population": "varp"
    }
    for aggregator, replacement in aggregator_chunk.items():
        matched_phrases = re.findall(aggregator, joined_token)
        for phrase in matched_phrases:
            joined_token = joined_token.replace(phrase, replacement)
            operators_map[replacement] = replacement

    tokens = joined_token.split(" ")
    for word in tokens:
        for key, val in miscellaneous_operators.items():
            # if word match operator -> add to operators mapping
            if word in val:
                operators_map[word] = key

    return operators_map, tokens


def literal_matching(tokens, internal_keywords):
    """
    :param tokens: tokens of user's query
    :param internal_keywords: internal keywords (list of schemas),
    Helper function: literal_map_word
    :return: map tokens to keywords (tokens contains all or part of keywords), list of remaining tokens
    """

    def literal_map_word(curr_word):
        if curr_word in internal_keywords:
            # extract exact map (token/ word in query exactly the same as keywords)
            return curr_word
        else:
            # check if token in query match a part of keywords
            for word in internal_keywords:
                if word.find(curr_word) != -1:  # check if token is a substring of an internal keyword
                    return word
        return None

    literal_map = dict()
    internal_keywords = set(internal_keywords)
    unmapped = []

    for token in tokens:
        mapped = literal_map_word(token)
        # map token
        if mapped is not None:
            if token in literal_map:
                literal_map[token].append(mapped)
            else:
                literal_map[token] = [mapped]

            if token in tokens:
                tokens.remove(token)
        elif '_' in token:
            # if token is a chunk and not able to map -> map by individual token
            for chunk_token in token.split("_"):
                chunk_mapped = literal_map_word(chunk_token)
                if chunk_mapped is not None:
                    if chunk_token in literal_map:
                        literal_map[chunk_token].append(chunk_mapped)
                    else:
                        literal_map[chunk_token] = [chunk_mapped]
                    if token in tokens:
                        tokens.remove(token)
                else:
                    unmapped.append(chunk_token)

    tokens = tokens + unmapped
    return literal_map, tokens


def pos_tagging(tokens):
    """Part-of-speech tagging for each token, tag notations:
        https://www.learntek.org/blog/categorizing-pos-tagging-nltk-python/
        return tagged list and chunked list
    """
    token_tag = pos_tag(tokens)

    token_tag_map = dict()
    for word, pos in token_tag:
        token_tag_map[word] = pos

    return token_tag_map


def chunking(tokens, operator_words, name_chunk):
    """get compound nouns from pos tagged words
        defined structure of compound nouns is: Noun + Adjective (optional)"""
    # filter out operator words
    tokens = [token for token in tokens if token not in operator_words]
    # filter out named entities
    chunking_tokens = [token for token in tokens if token not in name_chunk]

    token_tag = pos_tag(chunking_tokens)
    pattern = "NP:{<JJ>?<NN|NNP|NNS|NNPS>+<JJ>?}"

    regex_parser = RegexpParser(pattern)
    compound = regex_parser.parse(token_tag)

    # list storing words and compound words detected
    chunks = dict()
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

    chunked_tokens = joined_tokens.split(" ")

    return chunks, chunked_tokens


def named_entities(sentence):
    """Link to list of entities: https://stackoverflow.com/questions/59319207/ner-entity-recognition-country-filter
    :param processed_sentence - user query
    :return:
        - sentence - modified sentence (chunking named entities)
        - entity map - types of entities detected mapped to the set of words/phrases in sentence
        - names - list of names and type of name (geo location, person names, organization, etc.)"""
    processed_sentence = spacy_model(sentence)
    entity_map = dict()

    for ent in processed_sentence.ents:
        if ent.label_ in entity_map:
            entity_map[ent.label_].add(ent.text)
        else:
            entity_map[ent.label_] = {ent.text}

    names_tags = ["PERSON", "LOC", "ORG", "FAC", "GPE", "WORK_OF_ART", "LANGUAGE"]
    # create a set containing list of phrases that are names to avoid modifications (lemmed/autocorrect)
    name_map = dict()
    for label in names_tags:
        if label in entity_map:
            for name in entity_map[label]:
                name_phrase = name.replace(" ", "_")
                name_map[name_phrase] = label
                sentence = sentence.replace(name, name_phrase)

    # print(entity_map)
    # print("names", name_map)
    # print("Modified sentence", processed_sentence)
    return sentence, entity_map, name_map


def filter_sentence(tokens, operator_words):
    """Filter stopwords, comparisons from tokens of sentence"""
    # set of english stopwords
    stop_words = set(stopwords.words('english'))
    # get list of token and its tags
    token_tag_map = pos_tagging(tokens)

    filtered_sentence = []

    # filter out operator words and numeric values
    for word in tokens:
        if word in stop_words:
            continue
        if token_tag_map[word] == "CD":
            continue
        if word in operator_words:
            continue
        else:
            filtered_sentence.append(word)

    return filtered_sentence


def map_sentence(sentence, words):
    """Map keywords from sentence to word in the list words"""

    # get sentence with chunked named entities
    modified_sentence, entity_map, name_map = named_entities(sentence)
    sentence = modified_sentence
    sentence = preprocess(sentence)

    # Preprocess
    # stemmed = stem_sent(sentence)
    lemmed = lem_sent(sentence, name_map)

    all_tokens = spellcheck(lemmed, name_map)

    # mapped operators
    word_operator_map, remaining_tokens = mapped_operators(all_tokens)
    operators_words = set(word_operator_map.keys())

    all_tokens = remaining_tokens

    # chunking tokens
    chunks, chunked_tokens = chunking(all_tokens, operators_words, name_map)

    # filter stopwords, number
    filtered_sentence = filter_sentence(chunked_tokens, operators_words)

    # try literal mapping
    literal_mapped, remaining_tokens = literal_matching(filtered_sentence, words)
    mapped_literal_chunks = {key: val for key, val in chunks.items() if key in literal_mapped}

    # map remaining tokens using word2vec and wordnet
    avg_mapped = avg_map_word(remaining_tokens, words, name_map)
    mapped_chunks = {key: val for key, val in chunks.items() if key in avg_mapped}

    joined_tokens = " ".join(all_tokens)

    # group mapped chunks
    for key in mapped_literal_chunks.keys():
        joined_tokens = joined_tokens.replace(chunks[key], key)
    for key in mapped_chunks.keys():
        joined_tokens = joined_tokens.replace(chunks[key], key)

    all_tokens = joined_tokens.split(" ")
    # mapped items in order
    mapped_query = []
    stop_words = set(stopwords.words('english'))
    for token in all_tokens:
        if token in operators_words:
            mapped_query.append(word_operator_map[token])
        elif token in literal_mapped:
            mapped_query.append(literal_mapped[token][0])
        elif token in avg_mapped:
            mapped_query.append(avg_mapped[token][0])
        elif token in stop_words:
            continue
        else:
            mapped_query.append(token)

    return filtered_sentence, chunks, avg_mapped, operators_words, mapped_query


def mapped_types(mapped_query, metadata):
    mapped_stuffs = {
        "dimensions": [],
        "measures": [],
        "filters": []
    }

    filter = {
        "less", "greater", "not", "equal", "between", "and", "or", "group_by"
    }
    aggregator = {"count", "min", "max", "sum", "median", "stdev", "stdevp", "var", "varp", "mean", "list"}
    fields = set(metadata)

    last_added = deque()

    for token in mapped_query:
        if token in filter:
            mapped_stuffs["filters"].append(token)
            last_added.append("filters")
        elif token in aggregator:
            mapped_stuffs["measures"].append(token)
            last_added.append("measures")
        elif token in fields:
            if len(last_added) > 0:
                last_added_type = last_added.popleft()
                mapped_stuffs[last_added_type].append(token)
            else:
                mapped_stuffs["filters"].append(token)

            mapped_stuffs["dimensions"].append(token)
        else:
            # if not all 3 then itz filter value
            mapped_stuffs["filters"].append(token)

    return mapped_stuffs


def main():
    query = ["Average spending of customers in Tokyo, Japan",
             "Average spending of customers in Hanoi, Vietnam",
             "Average spending of customers in New York, America",
             "Average spending of customers before last November",
             "How much the customer Eric has spent in the last purchase",
             "Least profit from production company with sale between $20 million and $50 million",
             "Most profit from animation company that is not Disney from 2012 to 2020",
             "Least profit from animation company with income from $20 million to $50 million",
             "Most profit from animation company with income from $20 million - $50 million",
             "Movies that have higher profit than Frozen, Moana and Beauty and the Beast",
             "standard deviations of sale last quarter",
             "Show 10 cheapest products available",
             "show geo map of customers by country",
             "how many patients are over 50 years old",
             "count patients who have insurance and over 50 years old",
             "numbers of patients who have insurance and over 50 years old"]

    sample = ['id_', 'sale', 'country', 'client', 'age', 'insurance', 'production_company', 'date', 'city']

    # print(model.similarity("years-old", "age"))
    # mapped = [model.most_similar_to_given(x, sample) for x in filtered_sentence]
    for sentence in query:
        filtered, chunks, avg_mapped, operators, mapped_query = map_sentence(sentence, sample)

        print("Sentence: ", sentence)
        print(">> Mapped query: ", mapped_query)
        print("Sorted structure: ", mapped_types(mapped_query, sample))
        # Detailed output
        # print(">> Filtered: ", filtered)
        # print(">> Operators: \n", operators)
        # print(">> Chunks (tokens with compound nouns): \n", chunks)
        print(">> Mapped average of wordnet and word2vec: \n", avg_mapped)
        print()


if __name__ == '__main__':
    main()
