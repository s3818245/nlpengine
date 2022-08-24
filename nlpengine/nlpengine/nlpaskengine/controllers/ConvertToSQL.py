from NLPInputProcessor import NLPInputProcessor
from database import Database
from ExploreStructure import ExploreStructure

class ConvertToSQL:
    def __init__(self, meta_data):
        self.meta_data = meta_data

    def base_template(self, dimension):
        select_clause = ""
        if dimension["field_names"] == ['']:
            select_clause += "SELECT *"
        else:
            for i in dimension["field_names"]:
                if i == '': continue
                if select_clause == "":
                    select_clause += "SELECT " + i
                else:
                    select_clause += ", " + i
        from_clause = " FROM " + dimension["table_name"] 
        return (select_clause, from_clause)


    def inner_join_template(self, table_name_1, table_name_2, key_1, key_2):
        return f'{table_name_1} INNER JOIN {table_name_2} ON {table_name_1}.{key_1} = {table_name_2}.{key_2}'
    

    def where_template(self, filters):
        result = ""
        operators = {"less": "<", "greater": ">", "not": "not", "equal": "="}
        for i in filters:
            if result == "":
                result += " WHERE "
            for y in range(len(i["operators"])):
                if i["operators"][y] == "and" or i["operators"][y] == "or":
                    result += " " + i["operators"][y] + " "
                elif i["operators"][y] == "between":
                    val1, val2 =i["values"][y]
                    result += f'{i["table_name"]}.{i["field_name"]} ' + i["operators"][y] + val1 + " and " + val2
                else:
                    result += f'{i["table_name"]}.{i["field_name"]} ' + operators[i["operators"][y]] + " " + i["values"][y]
        return result

    def aggregate_template(self, measures):
        group_by = ""
        aggregate = ""
        for i in measures:
            if i["aggregation_type"] == "group_by":
                if group_by == "":
                    group_by += f' GROUP BY {i["table_name"]}.{i["field_name"]}'
                else:
                    group_by += f', {i["table_name"]}.{i["field_name"]}'
            else:
                if i["field_name"] == "":
                    i["field_name"] = self.meta_data[i["table_name"]]["primary_key"][2]
                if aggregate == "":
                    aggregate += f'{i["aggregation_type"]}({i["table_name"]}.{i["field_name"]})'
                else:
                    aggregate += f', {i["aggregation_type"]}({i["table_name"]}.{i["field_name"]})'
        return (aggregate, group_by)

def main():
    query = "List all products with sellingprice greater than 10 and less than 20"
    new_db = Database("1", "a2_s3802828", "postgres", "localhost", 5432, "postgres", None)
    nlp_processor = NLPInputProcessor(query, new_db.flatten_dimension())
    mapped_query, token_to_tag = nlp_processor.map_query()
    mapped_types = nlp_processor.mapped_types(mapped_query)
    print("Sentence: ", query)
    # print(">> Mapped query: ", mapped_query)
    print(">> Mapped with tags: ", token_to_tag)
    # print(">> Mapped types: ", mapped_types)
    explore_struct = ExploreStructure(mapped_query, new_db.fetch_metadata())
    print(explore_struct.explore_struct)
    print()

    convertToSQL = ConvertToSQL(new_db.fetch_metadata())
    aggregate, group_by = convertToSQL.aggregate_template(explore_struct.explore_struct["measures"])
    select_clause, from_clause =convertToSQL.base_template(explore_struct.explore_struct["dimensions"][0]) 
    where_clause = convertToSQL.where_template(explore_struct.explore_struct["filters"])
    sql_query = select_clause + aggregate + from_clause + where_clause + group_by
    print(sql_query)

if __name__ == '__main__':
    main()


    