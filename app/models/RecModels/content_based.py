import pickle
from ..ActiveLearning.active_learning import ActiveLearning

class ContentBased():
    def __init__(self) -> None:
        #self.dataframe = pd.read_csv("preprossed_data")
        self.similarity_matrix = None
        self.object_active_learning = ActiveLearning()

    def load_data(self):
        with open('similarity_ingredients.json', 'rb') as f:
            self.similarity_matrix = pickle.load(f)

    def create_sample(self, n_cluster, n):
        X, _ = self.object_active_learning.get_data(self.dataframe)
        dict_ = self.object_active_learning.create_diverse_sample(X, n_cluster, n)
        return list(dict_.keys()), list(dict_.values())

    def give_recommendation(self, data, index):
        self.load_data()
        index_recomm = self.similarity_matrix.loc[:,data.index].loc[index].sort_values(ascending=False).index.tolist()[1:6]
        recipe_recomm =  data['recipe_name'].loc[index_recomm].values
        result = {'Recipes':recipe_recomm,'Index':index_recomm}
        
        return result

    def recommend(self, favorite_list):
        recommend = []
        for i in favorite_list:
            for j in self.give_recommendation(self.dataframe, i)["Index"]:
                recommend.append(j)
        return recommend
