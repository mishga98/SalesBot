from mysql.connector import connect, Error


def write_to_db(data):
    result = "Произошла ошибка записи, проверьте формат данных"
    try:
        date, product, price, amount = data
        with connect(
                host="localhost",
                user="mishgauq_sales",
                password="Mishga17",
                database="mishgauq_sales",
        ) as connection:
            insert_query = """
            INSERT INTO sales (date, product, price, amount)
            VALUES
                ("{0}", "{1}", {2}, {3})    
            """.format(date, product, price, amount)
            with connection.cursor() as cursor:
                cursor.execute(insert_query)
                connection.commit()
        result = "Запись успешно добавлена!"
    except Error as e:
        print(e)
        return result
    return result


def get_stat(data):
    result = "Произошла ошибка запроса, проверьте формат данных"
    try:
        start_date, end_date = data
        with connect(
                host="localhost",
                user="mishgauq_sales",
                password="Mishga17",
                database="mishgauq_sales",
        ) as connection:
            res_msg = ""
            select_query = """ SELECT sum(summary), count(summary) 
                                FROM
                                    (SELECT *, price*amount as summary 
                                    FROM sales 
                                    WHERE date >= '{0}' and date <= '{1}') as production
                            """.format(start_date, end_date)

            print(select_query)
            with connection.cursor() as cursor:
                cursor.execute(select_query)
                result = cursor.fetchall()
                res_msg += "Сумма продаж за период: " + str(float(result[0][0]))
                res_msg += "\nКоличество продаж за период: " + str(int(result[0][1]))
            return res_msg

    except Error as e:
        print(e)
        return result
