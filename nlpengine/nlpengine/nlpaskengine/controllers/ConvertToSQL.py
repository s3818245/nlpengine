from tokenize import String
from xxlimited import new
from .NLPInputProcessor import NLPInputProcessor
from .database import Database
from .ExploreStructure import ExploreStructure

class ConvertToSQL:
    def __init__(self, meta_data, query):
        self.meta_data = meta_data
        self.query = query

    def base_template(self, dimension):
        select_clause = ""
        if dimension["field_names"] == [''] or " all " in self.query:
            select_clause += "SELECT *"
        else:
            for i in dimension["field_names"]:
                if i == '': continue
                if select_clause == "":
                    select_clause += "SELECT DISTINCT " + i
                else:
                    select_clause += ", " + i
        from_clause = " FROM " + dimension["table_name"] 
        return (select_clause, from_clause)


    def inner_join_template(self, table_name_1, table_name_2, key_1, key_2, has_table_name_1):
        if has_table_name_1:
            return f'{table_name_1} INNER JOIN {table_name_2} ON {table_name_1}.{key_1} = {table_name_2}.{key_2}'
        else:
            return f' INNER JOIN {table_name_2} ON {table_name_1}.{key_1} = {table_name_2}.{key_2}'

    def checkJoinCondition(self, dimensions, measures):
        if len(dimensions) > 1:
            inner_join_array = {}
            select_clause = ""
            for dimension in dimensions:
                if dimension["field_names"] == [''] or " all " in self.query:
                    if select_clause == "":
                        select_clause += "SELECT DISTINCT *"
                else:
                    for i in dimension["field_names"]:
                        if i == '': continue
                        if measures != []:
                            for y in measures:
                                if y["aggregation_type"] != "group_by":
                                    print("Aggregation type", y['aggregation_type'])
                                    # if y["field_name"] == i and dimension["table_name"] == y['table_name']:
                                    #     continue
                                    if select_clause == "":
                                        # if y['aggregation_type'] != 'max' and y['aggregation_type'] != 'min' and y['aggregation_type'] != 'avg' and y['aggregation_type'] != 'sum':
                                        #     select_clause += "SELECT DISTINCT " + i
                                        # else:
                                        select_clause += "SELECT DISTINCT "
                                    # else:
                                    #     # if y['aggregation_type'] != 'max' and y['aggregation_type'] != 'min' and y['aggregation_type'] != 'avg':
                                    #     # if select_clause == "SELECT DISTINCT ":
                                    #     #     select_clause += i
                                    #     # else:
                                    #     select_clause += ", "
                                else:
                                    if y["field_name"] == i and dimension["table_name"] == y['table_name']:
                                        if select_clause == "":
                                            select_clause += "SELECT DISTINCT " + i
                                        elif select_clause == "SELECT DISTINCT ":
                                            select_clause += i
                                        else:
                                            select_clause += ", " + i
                        else:
                            for i in dimensions:
                                table_name = ""
                                for y in i['field_names']:
                                    if y == '': continue
                                    if i["table_name"] != "" and y in self.meta_data[i["table_name"]]:
                                        table_name = f'{i["table_name"]}.'
                                    if select_clause == "":
                                        select_clause += f'SELECT DISTINCT {table_name}{y}'
                                    else:
                                        select_clause += f', {table_name}{y}'
                                    
            for i in range(len(dimensions)):
                for y in range(len(dimensions)):
                    if y == i: continue
                    for z in range(len(self.meta_data[dimensions[i]["table_name"]]["foreign_key"])):
                        foreign_key_element = self.meta_data[dimensions[i]["table_name"]]["foreign_key"][z]
                        if  foreign_key_element[3] == dimensions[y]["table_name"]:
                            if inner_join_array == {}:
                                inner_join_array[foreign_key_element[0]] = self.inner_join_template(dimensions[i]["table_name"], dimensions[y]["table_name"], foreign_key_element[2], foreign_key_element[4], True)
                            else:
                                inner_join_array[foreign_key_element[0]] = self.inner_join_template(dimensions[i]["table_name"], dimensions[y]["table_name"], foreign_key_element[2], foreign_key_element[4], False)

            from_clause = ""
            for i in inner_join_array.values():
                if from_clause == "":
                    from_clause += " FROM " + i
                else:
                    from_clause += " " + i
            return (select_clause, from_clause)
        elif measures != []:
            select_clause, from_clause = self.base_template(dimensions[0])
            select_clause = ""
            print("select" + select_clause + "hello")
            for i in dimensions[0]["field_names"]:
                if i == '': continue
                for y in measures:
                    if y["aggregation_type"] != "group_by":
                        print("Aggregation type", y['aggregation_type'])
                        # if y["field_name"] == i and dimensions[0]["table_name"] == y['table_name']:
                        #     continue
                        print(select_clause)
                        if select_clause == "":
                            # if y['aggregation_type'] != 'max' and y['aggregation_type'] != 'min' and y['aggregation_type'] != 'avg':
                            #     select_clause += "SELECT DISTINCT " + i
                            # else:
                            select_clause += "SELECT DISTINCT "
                        # else:
                        #     # if y['aggregation_type'] != 'max' and y['aggregation_type'] != 'min' and y['aggregation_type'] != 'avg':
                        #     #     if select_clause == "SELECT DISTINCT ":
                        #     #         select_clause += i
                        #     #     else:
                        #     select_clause += " "
                                
                    else:
                        if y["field_name"] == i and dimensions[0]["table_name"] == y['table_name']:
                            if select_clause == "":
                                select_clause += "SELECT DISTINCT " + i
                            elif select_clause == "SELECT DISTINCT ":
                                select_clause += i
                            else:
                                select_clause += ", " + i

            return (select_clause, from_clause)
        else:
            return self.base_template(dimensions[0])


    def where_template(self, filters):
        result = ""
        operators = {"less": "<", "greater": ">", "not": "not", "equal": "=", "equals": "="}
        for i in filters:
            if result == "":
                result += " WHERE "
            table_name = ""
            if i["table_name"] != "" and i["field_name"] in self.meta_data[i["table_name"]]:
                table_name = f'{i["table_name"]}.'
            for y in range(len(i["operators"])):
                print("OPERATOR 1: ", i["operators"][y])
                if i["operators"][y] == "and" or i["operators"][y] == "or" or i["operators"][y] == "not":
                    print("OPERATOR: ", i["operators"][y])
                    result += " " + i["operators"][y] + " "
                elif i["operators"][y] == "between":
                    val1, val2 =i["values"][y]
                    if "_" in val1:
                        val1 = val1.replace("_"," ")
                    if "_" in val2:
                        val2 = val2.replace("_"," ")
                    if val1.isnumeric() == False or val2.isnumeric() == False:
                        result += f'{table_name}{i["field_name"]} ' + i["operators"][y] + " '" + val1 + "' and '" + val2 + "'"
                    else:
                        result += f'{table_name}{i["field_name"]} ' + i["operators"][y] + " " + val1 + " and " + val2
                else:
                    val = i["values"][y]
                    if "_" in val:
                        val = val.replace("_"," ")
                    if val.isnumeric() == False:
                        result += f'{table_name}{i["field_name"]} ' + operators[i["operators"][y]] + " '" + val + "'"
                    else:
                        result += f'{table_name}{i["field_name"]} ' + operators[i["operators"][y]] + " " + val
        return result

    def aggregate_template(self, measures):
        group_by = ""
        aggregate = ""
        for i in measures:
            if i["aggregation_type"] == "group_by":
                table_name = ""
                if i["table_name"] != "" and i["field_name"] in self.meta_data[i["table_name"]]:
                    table_name = f'{i["table_name"]}.'
                    
                if group_by == "":
                    group_by += f' GROUP BY {table_name}{i["field_name"]}'
                else:
                    group_by += f', {table_name}{i["field_name"]}'
            else:
                if i["field_name"] == "":
                    i["field_name"] = self.meta_data[i["table_name"]]["primary_key"][0][2]
                if aggregate == "":
                    aggregate += f'{i["aggregation_type"]}({i["table_name"]}.{i["field_name"]})'
                else:
                    aggregate += f', {i["aggregation_type"]}({i["table_name"]}.{i["field_name"]})'
        return (aggregate, group_by)

def main():
    query = "List all saleinvoicedetail, product"
    new_db = Database("a2_s3802828", "postgres", "localhost", 5432, "postgres", None)
    nlp_processor = NLPInputProcessor(query, new_db.flatten_dimension())
    mapped_query, token_to_tag = nlp_processor.map_query()
    print(mapped_query)
    mapped_types = nlp_processor.mapped_types(mapped_query)
    print("Sentence: ", query)
    # print(">> Mapped query: ", mapped_query)
    print(">> Mapped with tags: ", token_to_tag)
    # print(">> Mapped types: ", mapped_types)
    explore_struct = ExploreStructure(mapped_query, new_db.fetch_metadata())
    print(explore_struct.explore_struct)

    convertToSQL = ConvertToSQL(new_db.fetch_metadata(), query)
    aggregate, group_by = convertToSQL.aggregate_template(explore_struct.explore_struct["measures"])
    select_clause, from_clause =convertToSQL.checkJoinCondition(explore_struct.explore_struct["dimensions"])
    where_clause = convertToSQL.where_template(explore_struct.explore_struct["filters"])

    if (aggregate != ""):
        sql_query = select_clause + ", " + aggregate + from_clause + where_clause + group_by
    else:
        sql_query = select_clause + aggregate + from_clause + where_clause + group_by

    print(sql_query)
    queryResult = new_db.run_query(sql_query)
    print(queryResult)

if __name__ == '__main__':
    main()


    