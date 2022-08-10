from NLPInputProcessor import NLPInputProcessor
from collections import deque
import re
import copy

DIMENSION_TEMPLATE = {"table_name": "",
                      "field_name": ""}
MEASURE_TEMPLATE = {"table_name": "",
                    "field_name": "",
                    "aggregation_type": ""}
FILTER_TEMPLATE = {"table_name": "",
                   "field_name": "",
                   "operator": "",
                   "value": ""}
RANGE_CHUNK = [
    'between_(\S*)_and_(\S*)',
    '(\S*)_to_(\S*)',
    'from_(\S*)_to_(\S*)',
    'from_(\S*)_-_(\S*)',
]

class NewExploreStructure:
    def __init__(self, mapped_list, metadata_struct={}):
        """
            assumed format of order:
            - Measure clause: aggregator phrase -> field(optional) -> table (e.g: Average age of customer)
            - Filter clause: (field -> table or table->field) ->filter phrase -> value(s) (e.g: Product with price over 50)

        :param mapped_list:
        :param metadata_struct:
        """
        self.mapped_list = mapped_list
        self.metadata = metadata_struct
        self.clause_order = deque()
        self.curr_dimension = None
        self.curr_measure = None
        self.curr_filter = None

        self.explore_struct = {
            "dimensions": [],
            "measures": [],
            "filters": []
        }
        self.last_table = None
        self.last_field = None
        self.last_filter = None

        self.generate_base_explore()
        self.beautify_explore()

    def generate_base_explore(self):
        for (mapped, mapped_type) in self.mapped_list:
            if mapped_type == "field":
                if mapped in self.metadata:
                    self.last_table = mapped
                else:
                    self.last_field = mapped

                if self.last_table and self.last_field:
                    self.explore_struct["dimensions"].append(
                        {"table_name": self.last_table,
                         "field_name": self.last_field}
                    )

                if self.curr_measure is not None:
                    #if a measure is currently generated -> field/table is part of measure clause
                    self.curr_measure.add_field(mapped)

            elif mapped_type == "aggregator":
                self.curr_measure = GenerateMeasureClause(self.metadata)
                self.curr_measure.add_aggregation(mapped)
                if self.last_table is not None:
                    self.curr_measure.add_field(self.last_table)

            elif mapped_type == "filter":
                self.curr_filter = GenerateFilterClause(self.metadata)
                self.curr_filter.add_field(self.last_field)
                self.curr_filter.add_field(self.last_table)

                extract_value = None
                if "_" in mapped:
                    extract_value = self.extract_from_chunk(mapped)

                filter_clause = self.curr_filter
                if extract_value is not None:
                    filter_clause.add_operator("between")
                    filter_clause.add_value(extract_value)
                    self.explore_struct["filters"].append(self.curr_filter.generated_clause)
                    self.curr_filter = None
                else:
                    filter_clause.add_operator(mapped)

                if mapped == "and" or mapped == "or":  # if filter is a connect word -> no value
                    filter_clause.add_value(' ')
                    self.explore_struct["filters"].append(self.curr_filter.generated_clause)
                    self.curr_filter = None
                else:
                    self.last_filter = mapped

            elif mapped_type == "value":
                if (self.last_field is None and self.last_table is None):
                    raise Exception("filter phrase not in required format")

                if self.curr_filter is None:
                    self.curr_filter = GenerateFilterClause(self.metadata)
                    if self.last_filter is None:
                        self.curr_filter.add_operator("equals")
                    else:
                        self.curr_filter.add_operator(self.last_filter)


                # if a value is specified without proper filter clause -> default filter is equals
                self.curr_filter.add_field(self.last_table)
                self.curr_filter.add_field(self.last_field)

                self.curr_filter.add_value(mapped)

                self.explore_struct["filters"].append(self.curr_filter.generated_clause)
                self.curr_filter = None

            elif mapped_type == "graph":
                self.explore_struct["visualization"] = mapped

            if (self.curr_measure is not None) and (self.curr_measure.is_completed()==True):
                self.explore_struct["measures"].append(self.curr_measure.generated_clause)
                self.curr_measure = None


            # print current state of explore struct and current token
            # print(f"current filter {self.curr_filter.generated_clause if self.curr_filter is not None else None}")
            # print(f"current measure {self.curr_measure.generated_clause if self.curr_measure is not None else None}")
            #
            # print(f"current token {mapped}. Current explore struct {self.explore_struct}")

    def beautify_explore(self):
        """
            Method to group dimensions in the same table and filters applied to the same columns together
        :return:
        """

        simplified_dimension = dict()
        simplified_filter = dict()

        for dimension_clause in self.explore_struct["dimensions"]:
            table = dimension_clause["table_name"]
            col = dimension_clause["field_name"]
            if table in simplified_dimension:
                simplified_dimension[table].append(col)
            else:
                simplified_dimension[table] = [col]

        self.explore_struct["dimensions"] = []
        for table, cols in simplified_dimension.items():
            self.explore_struct["dimensions"].append(
                {
                    "table_name": table,
                    "field_names": cols
                }
            )

        for filter_clause in self.explore_struct["filters"]:
            table = filter_clause["table_name"]
            col = filter_clause["field_name"]
            operator = filter_clause["operator"]
            value = filter_clause["value"]
            if (table, col) in simplified_filter:
                simplified_filter[(table, col)].append((operator, value))
            else:
                simplified_filter[(table, col)] = [(operator, value)]

        self.explore_struct["filters"] = []

        for field_applied, conditions in simplified_filter.items():
            table, col = field_applied
            added_filter = {
                "table_name": table,
                "field_name": col,
                "operators": [],
                "values": []
            }

            for operator, value in conditions:
                added_filter["operators"].append(operator)
                added_filter["values"].append(value)

            self.explore_struct["filters"].append(added_filter)


    def extract_from_chunk(self, phrase):
        # p = re.compile('name (.*?) is valid')
        found_value = None
        for pattern in RANGE_CHUNK:
            p = re.compile(pattern)
            found_values = p.findall(phrase)
            if len(found_values)>0:
                found_value = found_values[0]

        return found_value


class GenerateFilterClause:
    def __init__(self, metadata):
        self.metadata = metadata
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

    # def add_table(self, table):
    #     self.generated_clause["table_name"] = table

    def add_field(self, field):
        if field is None:
            return
        # self.generated_clause["table_name"] = field
        # self.generated_clause["field_name"] = field
        if field in self.metadata:  # if mapped is a key -> it's a table
            self.generated_clause["table_name"] = field
        else:
            self.generated_clause["field_name"] = field


    def add_operator(self, operator):
        self.generated_clause["operator"] = operator

    def add_value(self, value):
        self.generated_clause["value"] = value


class GenerateMeasureClause:
    def __init__(self, metadata):
        self.metadata = metadata
        self.generated_clause = copy.deepcopy(MEASURE_TEMPLATE)
        self.no_field_aggregator = {"count", "list"}

    def is_completed(self):
        completed = True

        if len(self.generated_clause["table_name"]) == 0:
            completed = False

        if self.generated_clause["aggregation_type"] not in self.no_field_aggregator \
                and len(self.generated_clause["field_name"]) == 0:
            completed = False

        if len(self.generated_clause["aggregation_type"]) == 0:
            completed = False

        return completed

    # def add_table(self, table):
    #     self.generated_clause["table_name"] = table

    def add_field(self, field):
        # self.generated_clause["table_name"] = field
        # self.generated_clause["field_name"] = field

        if field in self.metadata:  # if mapped is a key -> it's a table
            self.generated_clause["table_name"] = field
        else:
            self.generated_clause["field_name"] = field

    def add_aggregation(self, aggregation):
        self.generated_clause["aggregation_type"] = aggregation


def main():
    query = ["Average spending of customers in Hanoi, Vietnam",
             "Average spending of customers before last November",
             "Most profit from animation company that is not Disney from 2012 to 2020",
             "Most profit from animation company with gross profit from $20 million - $50 million",
             "Movies that have higher profit than titles Frozen, Moana and Beauty and the Beast",
             "standard deviations of sale last quarter",
             "show geo map of customers by country",
             "numbers of patients who is from New York and age over 50"]

    sample = ['sale', 'country', 'client', "name", 'age', 'production_company', 'date', 'city', "movie", "title"]
    sample_meta = {
        "client": {"city", "country", "age",  "date", "sale", "name"},
        "movie": {"title", "production_company", "sale"}
    }

    for sentence in query:
        nlp_processor = NLPInputProcessor(sentence, sample)
        mapped_query, token_to_tag = nlp_processor.map_query()
        mapped_types = nlp_processor.mapped_types(mapped_query)

        print("Sentence: ", sentence)
        print(">> Mapped query: ", mapped_query)
        # print(">> Mapped with tags: ", token_to_tag)
        # print(">> Mapped types: ", mapped_types)
        explore_struct = NewExploreStructure(mapped_query, sample_meta)
        print(explore_struct.explore_struct)
        print()

if __name__ == "__main__":
    main()