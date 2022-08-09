from NLPInputProcessor import NLPInputProcessor
from collections import deque
import re
import copy

DIMENSION_TEMPLATE = {"table_name": "",
                      "field_name": []}
MEASURE_TEMPLATE = {"table_name": "",
                    "field_name": "",
                    "aggregation_type": ""}
FILTER_TEMPLATE = {"table_name": "",
                   "field_name": "",
                   "operator": [],
                   "value": []}

mapped_types = {"filter", "aggregator", "field", "value", "graph"}

RANGE_CHUNK = [
    'between_(\S*)_and_(\S*)',
    'from_(\S*)_to_(\S*)',
    'from_(\S*)_-_(\S*)',
    '(\S*)_to_(\S*)',
]


class ExploreStructure:
    def __init__(self, mapped_list, metadata_struct={}):

        self.mapped_list = mapped_list
        self.metadata = metadata_struct
        self.clause_order = deque()
        self.explore_struct = {
            "dimensions": [],
            "measures": [],
            "filters": []
        }
        self.last_field = None

        for (mapped, mapped_type) in self.mapped_list:
            if mapped_type == "field":
                dimension_clause = GenerateDimensionClause()
                dimension_clause.add_field(mapped)
                # self.explore_struct["dimensions"].append(dimension_clause.generated_clause)
                self.last_field = mapped

                if len(self.clause_order) > 0:
                    self.clause_order[0].add_field(mapped)
                else:
                    #default clause is filter
                    filter_clause = GenerateFilterClause()
                    filter_clause.add_field(mapped)
                    self.clause_order.append(filter_clause)

            elif mapped_type == "aggregator":
                if len(self.clause_order) > 0:
                    if type(self.clause_order[0]) == GenerateMeasureClause:
                        self.clause_order[0].add_aggregator(mapped)
                else:
                    measure_clause = GenerateMeasureClause()
                    measure_clause.add_aggregation(mapped)
                    self.clause_order.append(measure_clause)

            elif mapped_type == "filter":
                extract_value = None
                if "_" in mapped:
                    extract_value = self.extract_from_chunk(mapped)

                # print(f"Detect filer {mapped}, clause order len {len((self.clause_order))}, type of first clause {}")
                if len(self.clause_order) > 0:
                    if type(self.clause_order[0]) == GenerateFilterClause:
                        if extract_value is not None:
                            self.clause_order[0].add_operator("between")
                            self.clause_order[0].add_value(extract_value)
                        else:
                            self.clause_order[0].add_operator(mapped)
                        if mapped == "and" or mapped == "or":  # if filter is a connect word -> no value
                            self.clause_order[0].add_value(' ')
                else:
                    filter_clause = GenerateFilterClause()
                    if extract_value is not None:
                        filter_clause.add_operator("between")
                        filter_clause.add_value(extract_value)
                    else:
                        filter_clause.add_operator(mapped)

                    if mapped == "and" or mapped == "or":  # if filter is a connect word -> no value
                        filter_clause.add_value(' ')
                    self.clause_order.append(filter_clause)

            elif mapped_type == "value":
                if len(self.clause_order) > 0:
                    self.clause_order[0].add_value(mapped)

            elif mapped_type == "graph":
                self.explore_struct["visualization"] = mapped

            self.update_clause_status()

    def extract_from_chunk(self, phrase):
        # p = re.compile('name (.*?) is valid')
        found_value = None
        for pattern in RANGE_CHUNK:
            p = re.compile(pattern)
            found_value = p.findall(phrase)
        return found_value

    def update_clause_status(self):
        if len(self.clause_order) > 0:
            if self.clause_order[0].is_completed():
                completed_clause = self.clause_order.popleft()

                if type(completed_clause) == GenerateMeasureClause:
                    self.explore_struct["measures"].append(completed_clause.generated_clause)
                elif type(completed_clause) == GenerateFilterClause:
                    self.explore_struct["filters"].append(completed_clause.generated_clause)


class GenerateDimensionClause:
    def __init__(self):
        self.generated_clause = copy.deepcopy(DIMENSION_TEMPLATE)

    def is_completed(self):
        completed = True

        if self.generated_clause["table_name"] == "" or len(self.generated_clause["field_name"]) == 0:
            completed = False
        return completed

    def add_field(self, field):
        self.generated_clause["table_name"] = field
        self.generated_clause["field_name"].append(field)


class GenerateMeasureClause:
    def __init__(self):
        self.generated_clause = copy.deepcopy(MEASURE_TEMPLATE)

    def is_completed(self):
        completed = True

        if self.generated_clause["table_name"] == "" or len(self.generated_clause["field_name"]) == 0:
            completed = False

        if len(self.generated_clause["aggregation_type"]) == 0:
            completed = False

        return completed

    def add_field(self, field):
        self.generated_clause["table_name"] = field
        self.generated_clause["field_name"] = field

    def add_aggregation(self, aggregation):
        self.generated_clause["aggregation_type"] = aggregation


class GenerateFilterClause:
    def __init__(self):
        self.generated_clause = copy.deepcopy(FILTER_TEMPLATE)
        self.last_operator = ""

    def is_completed(self):
        completed = True
        if self.generated_clause["table_name"] == "" or len(self.generated_clause["field_name"]) == 0:
            completed = False

        if len(self.generated_clause["operator"]) == 0 or (len(self.generated_clause["operator"])
                                                           != len(self.generated_clause["value"])):
            completed = False

        return completed

    def add_field(self, field):
        self.generated_clause["table_name"] = field
        self.generated_clause["field_name"] = field

    def add_operator(self, operator):
        self.generated_clause["operator"].append(operator)

    def add_value(self, value):
        self.generated_clause["value"].append(value)


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
        # print(">> Mapped with tags: ", token_to_tag)
        # print(">> Mapped types: ", mapped_types)
        explore_struct = ExploreStructure(mapped_query)
        print(explore_struct.explore_struct)
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
