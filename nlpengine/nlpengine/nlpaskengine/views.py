from django.shortcuts import render
from .controllers.NLPInputProcessor import NLPInputProcessor
from .controllers.database import Database
from .controllers.ExploreStructure import ExploreStructure
from .controllers.ConvertToSQL import ConvertToSQL
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# Create your views here.
new_db = None
@csrf_exempt
def get_query(request):
    global new_db
    query = request.GET.get('query')
    # new_db = request.session.get("db")
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
    select_clause, from_clause =convertToSQL.checkJoinCondition(explore_struct.explore_struct["dimensions"], explore_struct.explore_struct["measures"])
    where_clause = convertToSQL.where_template(explore_struct.explore_struct["filters"])

    if (aggregate != ""):
        sql_query = select_clause + ", " + aggregate + from_clause + where_clause + group_by
    else:
        sql_query = select_clause + aggregate + from_clause + where_clause + group_by

    print(sql_query)
    queryResult = new_db.run_query(sql_query)
    print(queryResult)
    result = {"result": queryResult.to_dict(), "rowCount": queryResult.shape[0], "sqlQuery": sql_query, "expStruct": explore_struct.explore_struct}
    print(result)
    return JsonResponse(result, safe = False)

def connect_database(request):
    db_name = request.GET.get('name')
    db_type = request.GET.get('type')
    db_host = request.GET.get('host')
    db_port = request.GET.get('port')
    db_user = request.GET.get('user')
    db_pass = request.GET.get('password')
    global new_db
    new_db = Database(db_name, db_type, db_host, db_port, db_user, db_pass)
    if new_db.get_connection() != None:
        return JsonResponse({"message": "Success"}, safe=False)
    else:
        new_db = None
        return JsonResponse({"message": "Failed"}, safe=False)


def disconnect_database(request):
    global new_db
    if new_db != None:
        new_db.close_connection()
        new_db = None
    return JsonResponse({"message": "Done"}, safe=False)



def get_metadata(request):
    global new_db
    if new_db != None:
        return JsonResponse({"metadata": new_db.fetch_dimension(), "db_name": new_db.get_name()}, safe=False)
    else:
        return JsonResponse({"metadata": None, "db_name": None}, safe=False)

def get_keyword_type(request):
    global new_db
    if new_db != None:
        query = request.GET.get('query')
        nlp_processor = NLPInputProcessor(query, new_db.flatten_dimension())
        mapped_query, token_to_tag = nlp_processor.map_query()
        return JsonResponse({"mapTag": token_to_tag}, safe=False)
    else:
        return JsonResponse({"mapTag": None}, safe=False)
