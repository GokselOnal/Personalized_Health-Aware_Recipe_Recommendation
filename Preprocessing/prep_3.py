import pandas as pd
import numpy as np
import warnings
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class PrepStep3():
    """
        A class to represent step3 of preprocessing

        Attributes
        ----------
        df: DataFrame
            DataFrame before the preprocessing operations
        common_ing: list
            list that contains n most common ingredients from all items
        cos_sim_data: DataFrame
            a matrix that represents cosine similarity for all items

        Methods
        ----------
        load_dataset()
            gets dataframe
        calculate_cosine_sim()
            calculates the cosine similarity of all items
        drop()
            drops some features
        classify_nutrition_value()
            classify nutritions into 4 different classes according to their values
        save_data()
            saves the preprocessed data
        ready_df()
            applies all other methods in this class in a sequence
        """

    def __int__(self):
        """
        Parameters
        ----------
        df: DataFrame
            DataFrame before the preprocessing operations
        common_ing: list
            list that contains n most common ingredients from all items
        cos_sim_data: DataFrame
            a matrix that represents cosine similarity for all items
        """
        self.df = None
        self.common_ing = None
        self.cos_sim_data = None

    def load_data(self):
        """ Gets dataframe """
        self.df = pd.read_csv("../preprossed_data.csv")

    def calculate_cosine_sim(self):
        """ Calculates the cosine similarity of all items """
        def del_caret(str_):
            return str_.replace("^", " ")

        X = self.df.ingredients.apply(del_caret)

        text_data = X
        model = SentenceTransformer('distilbert-base-nli-mean-tokens')
        embeddings = model.encode(text_data, show_progress_bar=True)
        self.cos_sim_data = pd.DataFrame(cosine_similarity(embeddings))

        with open('../similarity_ingredients.json', 'wb') as f:
            pickle.dump(self.cos_sim_data, f)

    def drop(self):
        """ Drops some features """
        self.df.drop("index", axis=1, inplace=True)

    def classify_nutrition_value(self):
        """ Classify nutritions into 4 different classes according to their values """
        def classifiy(index, nutrition_name):
            value = self.df.loc[index][nutrition_name]
            if value <= np.percentile(self.df[nutrition_name], 25):
                return "low"
            elif value >= np.percentile(self.df[nutrition_name], 75):
                return "high"
            else:
                if (value >= np.percentile(self.df[nutrition_name], 25)) and (value <= np.percentile(self.df[nutrition_name], 50)):
                    return "medium_low"
                elif (value >= np.percentile(self.df[nutrition_name], 50)) and (value <= np.percentile(self.df[nutrition_name], 75)):
                    return "medium_high"

        warnings.filterwarnings('ignore')
        nutrition_list = ["fat", "carbohydrates", "protein", "cholesterol", "sodium", "fiber"]
        for i in nutrition_list:
            name = i + "_class"
            self.df[name] = None
        for i in range(len(self.df)):
            for j in nutrition_list:
                name = j + "_class"
                self.df[name].iloc[i] = classifiy(i, j)

    def save_data(self):
        """ Saves the preprocessed data """
        #self.df.to_csv("../preprossed_data.csv", index=False)

    def ready_df(self):
        """ Applies all other methods in this class in a sequence """
        self.load_data()
        self.drop()
        self.classify_nutrition_value()
        self.save_data()
