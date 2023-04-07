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
            res_msg = "Отчет по продажам за период\n____________________\n"
            select_query = """ SELECT sum(summary), count(summary) 
                                FROM
                                    (SELECT *, price*amount as summary 
                                    FROM sales 
                                    WHERE date >= '{0}' and date <= '{1}') as production
                            """.format(start_date, end_date)
            select_query_top = """ SELECT product, sum(amount)  
                                   FROM sales 
                                   WHERE date >= '{0}' and date <= '{1}'
                                   GROUP BY product
                                   ORDER BY sum(amount) desc 
                                   LIMIT 3
                            """.format(start_date, end_date)
            with connection.cursor() as cursor:
                cursor.execute(select_query)
                result = cursor.fetchall()
                res_msg += "Сумма продаж: " + str(float(result[0][0]))
                res_msg += "\nКоличество продаж: " + str(int(result[0][1])) \
                           + "\n"

                cursor.execute(select_query_top)
                result = cursor.fetchall()
                res_msg += "\n\nТоп товаров по объему продаж:\n"

                for (index, row) in enumerate(result):
                    res_msg += "{0}. {1} - {2}\n".format(index + 1, row[0], float(row[1]))

            return res_msg

    except Error as e:
        print(e)
        return result
