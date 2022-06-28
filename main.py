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


def map_word(keyword, words, model):
    """Map keyword to words using wordnet and word2vec"""
    vec_mapped = model.most_similar_to_given(keyword, words)
    highest_similarity = 0
    net_mapped = ''

    keyword_synset = wn.synsets(keyword)[0]
    for word in words:
        word_synset = wn.synsets(word)[0]
        similarity = wn.path_similarity(keyword_synset, word_synset)
        if similarity > highest_similarity:
            highest_similarity = similarity
            net_mapped = word

    return vec_mapped, net_mapped


def avg_map_word(keyword, words, model):
    """Map keyword to the word (in list words) with highest average similarity value"""
    mapped = ''
    highest_similarity = 0

    keyword_synset = wn.synsets(keyword)[0]
    # map to internal word
    for word in words:
        vec_simi = model.similarity(keyword, word)
        word_synset = wn.synsets(word)[0]
        net_simi = wn.path_similarity(keyword_synset, word_synset)

        similarity_measurement_list = np.array([vec_simi, net_simi])
        avg_simi = np.average(similarity_measurement_list)

        if avg_simi > highest_similarity:
            highest_similarity = avg_simi
            mapped = word
    return mapped, highest_similarity


def mapped_operators(word):
    miscellaneous_operators = {
        "less": {"<", "less", "smaller", "below", "under", "before"},
        "greater": {">", "over", "bigger", "greater", "more", "above", "after"},
        "not": {"not"},
        "equal": {"equal", "="},
        "between": {"between"},
        "and": {"and"},
        "or": {"or"},
    }

    for key, val in miscellaneous_operators.items():
        if word in val:
            return word, key


def filter_sentence(tokens):
    """Filter stopwords, comparisons from tokens of sentence"""
    # set of english stopwords
    stop_words = set(stopwords.words('english'))

    # get list of words detected as operator
    operators = [mapped_operators(x) for x in tokens if mapped_operators(x) is not None]
    operators = {x for x, mapped in operators}

    # get list of token and its tags
    token_tag_map, chunks = pos_tagging(tokens)

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
    pattern = "NP:{<JJ>?<NN|NNP|NNS|NNPS>+<JJ>?}"

    regex_parser = RegexpParser(pattern)
    compound = regex_parser.parse(token_tag)

    # list storing words and compound words detected
    chunks = []
    # iterate each branch of a tree
    for branch in compound:
        # if branch is another subtree -> it is a compound nouns
        if type(branch) == nltk.Tree:
            chunks.append("_".join([token for token, pos in branch.leaves()]))
        else:
            # if not a subtree -> tuple of (word, pos)
            word, pos = branch
            chunks.append(word)

    token_tag_map = dict()
    for word, pos in token_tag:
        token_tag_map[word] = pos

    return token_tag_map, chunks


def map_sentence(sentence, words):
    speller = Speller()
    model = get_word2vec()

    """Map keywords from sentence to word in the list words"""
    # stemmed = stem_sent(sentence)
    lemmed = lem_sent(sentence)
    # spell check lemmatized sentence
    spell_check = speller(lemmed)
    all_tokens = nltk.word_tokenize(spell_check)

    # mapped operators
    operators = [mapped_operators(x) for x in all_tokens if mapped_operators(x) is not None]

    tokens_tag, chunks = pos_tagging(all_tokens)

    # filter stopwords and comparisons number
    filtered_sentence = filter_sentence(all_tokens)

    mapped = [map_word(x, words, model) for x in filtered_sentence]
    avg_mapped = [avg_map_word(x, words, model) for x in filtered_sentence]

    return filtered_sentence, chunks, mapped, avg_mapped, operators


def main():
    speller = Speller()
    model = get_word2vec()
    query = ["Average spending of customers in each country",
             "Average spending of customers before last November",
             "Most profit from production company in Vietnam",
             "count all people who have insurance and over 50 years old"]

    sample = ['sale', 'mean', 'country', 'client', 'age', 'count', 'id', 'insurance']

    # mapped = [model.most_similar_to_given(x, sample) for x in filtered_sentence]
    for sentence in query:
        filtered, chunks, mapped, avg_mapped, operators = map_sentence(sentence, sample)
        print("Sentence: ", sentence)
        print(">> Filtered: ", filtered)
        print(">> Operators: \n", operators)
        print(">> Chunks (tokens with compound nouns): \n", chunks)
        print(">> Mapped by wordnet vs word2vec: \n", mapped)
        print(">> Mapped average of wordnet and word2vec: \n", avg_mapped)
        print()


if __name__ == '__main__':
    main()
