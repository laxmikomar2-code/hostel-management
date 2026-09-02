import mysql.connector


def get_connection():
    connection = mysql.connector.connect(
        host="host.docker.internal",
        port=3306,
        user="root",
        password="root",
        database="hostel_management"
    )

    return connection


try:
    connection = get_connection()
    print("MySQL Database Connected Successfully!")
    connection.close()

except mysql.connector.Error as error:
    print("MySQL Connection Failed:", error)