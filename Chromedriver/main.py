from src.db.DBHelper import DBHelper

db = DBHelper.DBHelper("Data_of_films_and_actors.db")
data2 = []
# lst = db.fetch_roles_actor("Фрэнк Дарабонт")
another_actors = db.fetch_another_actor(" Годзилла ")
print(another_actors)
# data = [(tuple[0]+tuple[1], tuple[3]) for tuple in lst]
# for i in range(50):
#     data2.append(data[i])
# print(data2)
# G = nx.Graph(data2)
# pos = nx.spring_layout(G, k=2)
# nx.draw(G, pos=pos, with_labels=True)
# plt.show()