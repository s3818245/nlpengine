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
import numpy as np
import os

# Uncomment to download nltk packages
# nltk.download('omw-1.4')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')

# define root path to current directory
root = os.getcwd()


# comparison words
# comparison = ['under', 'over', 'and', 'or', 'below', 'between', 'above', 'after', 'more', 'from', 'to']
# comparison = set(comparison)


# stemming - Snowball stemmer
def stem_sent(sentence):
    """Stem sentence to convert to its base form"""

    sentence = sentence.lower()
    # stemmer = SnowballStemmer("english")
    stemmer = PorterStemmer()
    stemmed = [stemmer.stem(word) for word in nltk.word_tokenize(sentence)]
    return " ".join(stemmed)


# lemmatization - WordNetLemmatizer
def lem_sent(sentence):
    """Lemmatize sentence to convert to its base form"""
    sentence = sentence.lower()
    lemmatizer = WordNetLemmatizer()
    lemmatized = [lemmatizer.lemmatize(word) for word in nltk.word_tokenize(sentence)]
    return " ".join(lemmatized)


def get_word2vec():
    """Get word2vec model"""
    model = None
    if not os.path.isfile("./word2vec.model"):
        # model = gensim.downloader.load('fasttext-wiki-news-subwords-300')
        model = gensim.downloader.load('word2vec-google-news-300')
        model.save("word2vec.model")
    else:
        model = KeyedVectors.load("word2vec.model")
    return model


def map_word(keywords, words, model):
    vec_map = dict()
    net_map = dict()

    for keyword in keywords:
        """Map keyword to words using wordnet and word2vec"""
        try:
            vec_mapped = model.most_similar_to_given(keyword, words)
        except:
            vec_mapped = None
        highest_similarity = 0
        net_mapped = ''

        keyword_synset = wn.synsets(keyword)[0]
        for word in words:
            try:
                word_synset = wn.synsets(word)[0]
                similarity = wn.path_similarity(keyword_synset, word_synset)
            except:
                similarity = 0

            if similarity > highest_similarity:
                highest_similarity = similarity
                net_mapped = word

        vec_map[keyword] = vec_mapped
        net_map[keyword] = net_mapped

    return vec_map, net_map


def avg_map_word(keywords, chunks, words, model):
    avg_map = dict()

    # try mapping by chunks
    for chunk in chunks.keys():
        chunk_mapped = ''
        highest_similarity = 0

        # map to internal word
        for word in words:
            try:
                vec_simi = model.similarity(chunk, word)
            except:
                vec_simi = 0
            try:
                keyword_synset = wn.synsets(chunk)[0]
                word_synset = wn.synsets(word)[0]
                net_simi = wn.path_similarity(keyword_synset, word_synset)
            except:
                net_simi = 0

            similarity_measurement_list = np.array([vec_simi, net_simi])
            avg_simi = np.average(similarity_measurement_list)
            if avg_simi > highest_similarity:
                highest_similarity = avg_simi
                chunk_mapped = word

        if len(chunk_mapped) > 0:
            for token in chunks[chunk]:
                if token in keywords:
                    keywords.remove(token)
            avg_map[chunk] = chunk_mapped

    """Map keyword to the word (in list words) with highest average similarity value"""
    for keyword in keywords:
        mapped = ''
        highest_similarity = 0

        # map to internal word
        for word in words:
            try:
                vec_simi = model.similarity(keyword, word)
            except:
                vec_simi = 0
            try:
                keyword_synset = wn.synsets(keyword)[0]
                word_synset = wn.synsets(word)[0]
                net_simi = wn.path_similarity(keyword_synset, word_synset)
            except:
                net_simi = 0

            similarity_measurement_list = np.array([vec_simi, net_simi])
            avg_simi = np.average(similarity_measurement_list)
            if avg_simi > highest_similarity:
                highest_similarity = avg_simi
                mapped = word
        avg_map[keyword] = (mapped, highest_similarity)
    return avg_map


def mapped_operators(tokens):
    miscellaneous_operators = {
        "less": {"<", "less", "smaller", "below", "under", "before"},
        "greater": {">", "over", "bigger", "greater", "more", "above", "after"},
        "not": {"not"},
        "equal": {"equal", "="},
        "between": {"between"},
        "and": {"and"},
        "or": {"or"},
        "mean": {"mean", "average"}
    }

    operators_map = dict()
    for word in tokens:
        for key, val in miscellaneous_operators.items():
            if word in val:
                operators_map[word] = key

    return operators_map


def literal_matching(tokens, chunks, internal_words):
    """
    :param chunks: compound nouns found in query
    :param tokens: tokens of user's query
    :param internal_words: internal keywords (list of schemas),
    :return: map tokens to keywords (tokens contains all or part of keywords)
    """

    literal_map = dict()

    internal_words = set(internal_words)
    for chunk in chunks.keys():
        if chunk in internal_words:
            literal_map[chunk] = chunk
            # removed mapped chunk from list of words
            for token in chunks[chunk]:
                if token in tokens:
                    tokens.remove(token)
        else:
            splitted_chunk = chunk.split("_")
            for token in splitted_chunk:
                if token in internal_words:
                    literal_map[chunk] = token

    for token in tokens:
        if token in internal_words:
            # extract exact map (token/ word in query exactly the same as keywords)
            literal_map[token] = [token]
            tokens.remove(token)
        else:
            # check if token in query match a part of keywords
            for word in internal_words:
                if word.find(token) != -1:  # check if token is a substring
                    tokens.remove(token)
                    # if there is already a word mapped with token -> token can be mapped with multiple keywords
                    if token in literal_map:
                        literal_map[token].append(word)
                    else:
                        literal_map[token] = [word]

    return literal_map, tokens


def pos_tagging(tokens):
    """Part-of-speech tagging for each token, tag notations:
        CC | Coordinating conjunction |
        CD | Cardinal number |
        DT | Determiner |
        EX | Existential there |
        FW | Foreign word |
        IN | Preposition or subordinating conjunction |
        JJ | Adjective |
        JJR | Adjective, comparative |
        JJS | Adjective, superlative |
        LS | List item marker |
        MD | Modal |
        NN | Noun, singular or mass |
        NNS | Noun, plural |
        NNP | Proper noun, singular |
        NNPS | Proper noun, plural |
        PDT | Predeterminer |
        POS | Possessive ending |
        PRP | Personal pronoun |
        PRP$ | Possessive pronoun |
        RB | Adverb |
        RBR | Adverb, comparative |
        RBS | Adverb, superlative |
        RP | Particle |
        SYM | Symbol |
        VB | Verb, base form |
        VBD | Verb, past tense |
        VBG | Verb, gerund or present participle |
        VBN | Verb, past participle |
        VBP | Verb, non-3rd person singular present |
        VBZ | Verb, 3rd person singular present |
        WDT | Wh-determiner |
        WP | Wh-pronoun |
        WP$ | Possessive wh-pronoun |
        WRB | Wh-adverb |

        return tagged list and chunked list
    """
    token_tag = pos_tag(tokens)
    # pattern = "NP:{<JJ>?<NN|NNP|NNS|NNPS>+<JJ>?}"
    #
    # regex_parser = RegexpParser(pattern)
    # compound = regex_parser.parse(token_tag)
    #
    # # list storing words and compound words detected
    # chunks = []
    # # iterate each branch of a tree
    # for branch in compound:
    #     # if branch is another subtree -> it is a compound nouns
    #     if type(branch) == nltk.Tree:
    #         chunks.append("_".join([token for token, pos in branch.leaves()]))
    #     else:
    #         # if not a subtree -> tuple of (word, pos)
    #         word, pos = branch
    #         chunks.append(word)

    token_tag_map = dict()
    for word, pos in token_tag:
        token_tag_map[word] = pos

    return token_tag_map


def chunking(tokens):
    """get compound nouns from pos tagged words
        defined structure of compound nouns is: Noun + Adjective (optional)"""
    token_tag = pos_tag(tokens)
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
        # else:
        #     # if not a subtree -> tuple of (word, pos)
        #     word, pos = branch
        #     chunks.append(word)
    return chunks


def filter_sentence(tokens, operators):
    """Filter stopwords, comparisons from tokens of sentence"""
    # set of english stopwords
    stop_words = set(stopwords.words('english'))

    # # get list of words detected as operator
    # word_operator_map = mapped_operators(tokens)
    # operators = word_operator_map.keys()

    # get list of token and its tags
    token_tag_map = pos_tagging(tokens)

    filtered_sentence = []

    # filter out operator words and numeric values
    for word in tokens:
        if word in stop_words:
            continue
        if word in operators:
            continue
        if token_tag_map[word] == "CD":
            continue
        else:
            filtered_sentence.append(word)

    return filtered_sentence


def map_sentence(sentence, words):
    """Map keywords from sentence to word in the list words"""

    # Initialize spell checker and word2vec
    speller = Speller()
    model = get_word2vec()

    # Preprocess
    # stemmed = stem_sent(sentence)
    lemmed = lem_sent(sentence)
    # spell check lemmatized sentence
    spell_check = speller(lemmed)
    all_tokens = nltk.word_tokenize(spell_check)

    # mapped operators
    word_operator_map = mapped_operators(all_tokens)
    operators_words = set(word_operator_map.keys())

    # chunking tokens
    chunks = chunking(all_tokens)

    # filter stopwords and comparisons, number
    filtered_sentence = filter_sentence(all_tokens, operators_words)

    # try literal mapping
    literal_mapped, remaining_tokens = literal_matching(filtered_sentence, chunks, words)
    # print(f"Literal mapped: {literal_mapped}\n, Remaining tokens: {remaining_tokens}")

    mapped_literal_chunks = {key: val for key, val in chunks.items() if key in literal_mapped}

    # map remaining tokens using word2vec and wordnet
    mapped = [x for x in map_word(remaining_tokens, words, model)]
    avg_mapped = avg_map_word(remaining_tokens, chunks, words, model)

    mapped_chunks = {key: val for key, val in chunks.items() if key in avg_mapped}

    # group mapped chunks
    for key in mapped_literal_chunks.keys():
        sentence.replace(chunks[key], key)

    print("Mapped chunks", mapped_chunks)
    for key in mapped_chunks.keys():
        sentence.replace(chunks[key], key)

    # mapped items in order
    mapped_query = []
    for token in all_tokens:
        if token in literal_mapped:
            mapped_query.append(literal_mapped[token][0])
        elif token in operators_words:
            mapped_query.append(word_operator_map[token])
        elif token in avg_mapped:
            mapped_query.append(avg_mapped[token][0])
        else:
            mapped_query.append(token)

    # mapped_query = " ".join(mapped_query)

    return filtered_sentence, chunks, mapped, avg_mapped, operators_words, mapped_query


def main():
    speller = Speller()
    model = get_word2vec()
    query = ["Average spending of customers in each country",
             "Average spending of customers before last November",
             "Most profit from company in Vietnam",
             "count all people who have insurance and over 50 years old"]

    sample = ['sale', 'mean', 'country', 'client', 'age', 'count', 'insurance', 'production_company']

    # mapped = [model.most_similar_to_given(x, sample) for x in filtered_sentence]
    for sentence in query:
        filtered, chunks, mapped, avg_mapped, operators, mapped_query = map_sentence(sentence, sample)

        print("Sentence: ", sentence)
        print(">> Mapped query: ", mapped_query)

        # Detailed output
        # print(">> Filtered: ", filtered)
        # print(">> Operators: \n", operators)
        # print(">> Chunks (tokens with compound nouns): \n", chunks)
        # print(">> Mapped by wordnet vs word2vec: \n", mapped)
        # print(">> Mapped average of wordnet and word2vec: \n", avg_mapped)
        print()


if __name__ == '__main__':
    main()
