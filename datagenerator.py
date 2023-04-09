import random
from database import write_to_db_multiple
data = []
for i in range(1000):
    date = random.randint(1,28)
    month = random.randint(1,12)
    year = random.randint(2022,2023)
    date = "{0}-{1}-{2}".format(year, month, date)
    product = random.choice(["Соль", "Сахар", "Перец", "Лук", "Чеснок"])
    price = random.randint(50, 200)
    amount = random.randint(1, 40)
    data.append([date, product, price, amount])

write_to_db_multiple(data)
