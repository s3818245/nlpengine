import psycopg2


class Database:
    def __init__(self, id, db_name, db_type, db_host, db_port, db_user, db_password):
        self.__id = id
        self.__db_name = db_name
        self.__db_type = db_type
        self.__db_host = db_host
        self.__db_port = db_port
        self.__db_user = db_user
        self.__db_password = db_password
        try:

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.__db_connection = psycopg2.connect(host=self.__db_host, database=self.__db_name, user=self.__db_user,
                                                    password=self.__db_password, port=self.__db_port)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def get_connection(self):
        return self.__db_connection

    def close_connection(self):
        if self.__db_connection is not None:
            self.__db_connection.close()
            print('Database connection closed.')

    def fetch_dimension(self):
        # create a cursor
        cur = self.__db_connection.cursor()

        result = dict()
        cur.execute("""SELECT * FROM information_schema.tables
               WHERE table_schema = 'public'""")
        tables = [tab[2] for tab in cur.fetchall()]
        for table in tables:
            cur.execute('SELECT * FROM ' + table)
            column_names = [desc[0] for desc in cur.description]
            result[table] = column_names
        # close the communication with the PostgreSQL
        cur.close()
        return result

    def query_relationship(self):
        # create a cursor
        cur = self.__db_connection.cursor()

        result = dict()
        cur.execute("""SELECT * FROM information_schema.tables
                       WHERE table_schema = 'public'""")
        tables = [tab[2] for tab in cur.fetchall()]
        for table in tables:
            cur.execute("""SELECT tc.constraint_name, tc.table_name, kcu.column_name, 
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name 
                        FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                          ON ccu.constraint_name = tc.constraint_name
                        WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name='""" + table + "';")
            foreign_keys = cur.fetchall()
            cur.execute("""SELECT tc.constraint_name, tc.table_name, kcu.column_name, 
                                    ccu.table_name AS foreign_table_name,
                                    ccu.column_name AS foreign_column_name 
                                    FROM 
                                    information_schema.table_constraints AS tc 
                                    JOIN information_schema.key_column_usage AS kcu
                                      ON tc.constraint_name = kcu.constraint_name
                                    JOIN information_schema.constraint_column_usage AS ccu
                                      ON ccu.constraint_name = tc.constraint_name
                                    WHERE constraint_type = 'PRIMARY KEY' AND tc.table_name='""" + table + "';")
            pk_keys = cur.fetchall()
            result[table] = {"foreign_key": foreign_keys, "primary_key": pk_keys}
        # close the communication with the PostgreSQL
        cur.close()
        return result

    def fetch_metadata(self):
        dimension = self.fetch_dimension()
        relationship = self.query_relationship()
        for aKey in relationship.keys():
            relationship[aKey]["columns"] = dimension[aKey]
        return relationship
    
    def flatten_dimension(self):
        dimensions = self.fetch_dimension()
        flatten_dimensions = []
        for key, val in dimensions.items():
            flatten_dimensions.append(key)
            flatten_dimensions = flatten_dimensions + val
        return flatten_dimensions
        


if __name__ == '__main__':
    new_db = Database("1", "a2_s3802828", "postgres", "localhost", 5432, "postgres", None)
    print(new_db.flatten_dimension())
