import psycopg2


try:
    connection = psycopg2.connect(user="postgres",
                                  password="postgres",
                                  host="localhost",
                                  database="network_project_db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Client;")
    version=cursor.fetchall()
    print(version)
    cursor.close()
    connection.close()
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)    

