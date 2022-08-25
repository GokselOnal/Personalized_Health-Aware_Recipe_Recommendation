import pandas as pd
import warnings
import json


class PrepStep1():
    """
    A class to represent step1 of preprocessing

    Attributes
    ----------
    df: DataFrame
        DataFrame before the preprocessing operations

    Methods
    ----------
    load_dataset()
        gets dataframe
    process_duration_direction()
        applies preprocessing operations for duration and direction features
    process_nutritions()
        applies preprocessing operations for nutritions features
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
        """
        self.df = None

    def load_dataset(self):
        """ Gets dataframe from the csv """
        self.df = pd.read_csv("../raw-data_recipe.csv")
        self.df = self.df.drop(index=28799)
        self.df = self.df.reset_index()

    def process_duration_direction(self):
        """ Applies preprocessing operations for duration and direction features """
        def process(str_):
            dict_ = {"Prep": None, "Cook": None, "Ready In": None, "Directions": None}
            arr = str_.split("\\n")
            arr[0] = arr[0][17:]
            directions = ""
            k = -11
            if "Ready In" not in str_:
                for j in range(len(arr)):
                    directions += arr[j]
                dict_["Directions"] = directions
                return dict_
            for i in range(len(arr)):
                if arr[i] == "Prep":
                    dict_["Prep"] = arr[i + 1]
                elif arr[i] == "Cook":
                    dict_["Cook"] = arr[i + 1]
                elif arr[i] == "Ready In":
                    dict_["Ready In"] = arr[i + 1]
                    k = i + 1
                if i == k:
                    for j in range(k + 1, len(arr)):
                        directions += arr[j]
                    dict_["Directions"] = directions
            return dict_

        list_prep, list_cook, list_ready_in, list_directions = [], [], [], []
        for i in range(self.df.shape[0]):
            dict_ = process(self.df.cooking_directions.loc[i])
            list_prep.append(dict_["Prep"])
            list_cook.append(dict_["Cook"])
            list_ready_in.append(dict_["Ready In"])
            list_directions.append(dict_["Directions"])
        self.df["prep"] = list_prep
        self.df["cook"] = list_cook
        self.df["ready_in"] = list_ready_in
        self.df["directions"] = list_directions

    def process_nutritions(self):
        """ Applies preprocessing operations for nutritions features """
        warnings.filterwarnings('ignore')
        list_calcium = pd.Series([])
        list_calories = pd.Series([])
        list_calories_fat = pd.Series([])
        list_carbohydrates = pd.Series([])
        list_Cholesterol = pd.Series([])
        list_fiber = pd.Series([])
        list_fat = pd.Series([])
        list_folate = pd.Series([])
        list_iron = pd.Series([])
        list_magnesium = pd.Series([])
        list_niacin = pd.Series()
        list_potassium = pd.Series([])
        list_protein = pd.Series([])
        list_saturatedfat = pd.Series([])
        list_sodium = pd.Series([])
        list_sugars = pd.Series([])
        list_thiamin = pd.Series([])
        list_vitaminA = pd.Series([])
        list_vitaminB6 = pd.Series([])
        list_vitaminC = pd.Series([])

        list_total = []

        names = []
        k = 0
        for i in self.df.nutritions:
            for j in range(len(self.df.nutritions[0].split("},"))):
                if j == len(self.df.nutritions[0].split("},")) - 1:
                    str_ = "{" + i.split("},")[j].split(": {u")[1].replace("'", "\"").replace("u\"", "\"").replace(
                        "True", '"True"').replace("False", '"False"').replace("None", '"None"') + "}"
                    dict_ = json.loads(str_[:-2])
                else:
                    str_ = "{" + i.split("},")[j].split(": {u")[1].replace("'", "\"").replace("u\"", "\"").replace(
                        "True", '"True"').replace("False", '"False"').replace("None", '"None"') + "}"
                    dict_ = json.loads(str_)
                names.append(dict_["name"])
                if dict_["name"] == "Calcium":
                    d = {k: dict_["percentDailyValue"]}
                    list_calcium = list_calcium.append(pd.Series(d))
                if dict_["name"] == "Calories":
                    d = {k: dict_["percentDailyValue"]}
                    list_calories = list_calories.append(pd.Series(d))

                if dict_["name"] == "Calories from Fat":
                    d = {k: dict_["percentDailyValue"]}
                    list_calories_fat = list_calories_fat.append(pd.Series(d))

                if dict_["name"] == "Carbohydrates":
                    d = {k: dict_["percentDailyValue"]}
                    list_carbohydrates = list_carbohydrates.append(pd.Series(d))

                if dict_["name"] == "Cholesterol":
                    d = {k: dict_["percentDailyValue"]}
                    list_Cholesterol = list_Cholesterol.append(pd.Series(d))

                if dict_["name"] == "Dietary Fiber":
                    d = {k: dict_["percentDailyValue"]}
                    list_fiber = list_fiber.append(pd.Series(d))

                if dict_["name"] == "Fat":
                    d = {k: dict_["percentDailyValue"]}
                    list_fat = list_fat.append(pd.Series(d))

                if dict_["name"] == "Folate":
                    d = {k: dict_["percentDailyValue"]}
                    list_folate = list_folate.append(pd.Series(d))

                if dict_["name"] == "Iron":
                    d = {k: dict_["percentDailyValue"]}
                    list_iron = list_iron.append(pd.Series(d))

                if dict_["name"] == "Magnesium":
                    d = {k: dict_["percentDailyValue"]}
                    list_magnesium = list_magnesium.append(pd.Series(d))

                if dict_["name"] == "Niacin Equivalents":
                    d = {k: dict_["percentDailyValue"]}
                    list_niacin = list_niacin.append(pd.Series(d))

                if dict_["name"] == "Potassium":
                    d = {k: dict_["percentDailyValue"]}
                    list_potassium = list_potassium.append(pd.Series(d))

                if dict_["name"] == "Protein":
                    d = {k: dict_["percentDailyValue"]}
                    list_protein = list_protein.append(pd.Series(d))

                if dict_["name"] == "Saturated Fat":
                    d = {k: dict_["percentDailyValue"]}
                    list_saturatedfat = list_saturatedfat.append(pd.Series(d))

                if dict_["name"] == "Sodium":
                    d = {k: dict_["percentDailyValue"]}
                    list_sodium = list_sodium.append(pd.Series(d))

                if dict_["name"] == "Sugars":
                    d = {k: dict_["percentDailyValue"]}
                    list_sugars = list_sugars.append(pd.Series(d))

                if dict_["name"] == "Thiamin":
                    d = {k: dict_["percentDailyValue"]}
                    list_thiamin = list_thiamin.append(pd.Series(d))

                if dict_["name"] == "Vitamin A - IU":
                    d = {k: dict_["percentDailyValue"]}
                    list_vitaminA = list_vitaminA.append(pd.Series(d))

                if dict_["name"] == "Vitamin B6":
                    d = {k: dict_["percentDailyValue"]}
                    list_vitaminB6 = list_vitaminB6.append(pd.Series(d))

                if dict_["name"] == "Vitamin C":
                    d = {k: dict_["percentDailyValue"]}
                    list_vitaminC = list_vitaminC.append(pd.Series(d))
            k += 1
        total = [list_niacin, list_sugars, list_sodium, list_carbohydrates, list_vitaminB6, list_calories, list_thiamin,
                 list_fat, list_folate, list_calcium, list_calories_fat, list_Cholesterol, list_fiber, list_iron,
                 list_magnesium, list_potassium, list_protein, list_saturatedfat, list_vitaminA, list_vitaminC]

        self.df["niacins"] = list_niacin
        self.df["sugars"] = list_sugars
        self.df["sodium"] = list_sodium
        self.df["carbohydrates"] = list_carbohydrates
        self.df["vitamin_B6"] = list_vitaminB6
        self.df["calories"] = list_calories
        self.df["thiamin"] = list_thiamin
        self.df["fat"] = list_fat
        self.df["folate"] = list_folate
        self.df["calcium"] = list_calcium
        self.df["calories_fat"] = list_calories_fat
        self.df["cholesterol"] = list_Cholesterol
        self.df["fiber"] = list_fiber
        self.df["iron"] = list_iron
        self.df["magnesium"] = list_magnesium
        self.df["potassium"] = list_potassium
        self.df["protein"] = list_protein
        self.df["saturatedfat"] = list_saturatedfat
        self.df["vitaminA"] = list_vitaminA
        self.df["vitaminC"] = list_vitaminC

        del self.df["index"]
        self.df.drop("calories_fat", axis=1, inplace=True)

    def save_data(self):
        """ Saves the preprocessed data """
        #self.df.to_csv("../preprossed_data.csv", index=False)

    def ready_df(self):
        """ Applies all other methods in this class in a sequence """
        self.load_dataset()
        self.process_duration_direction()
        self.process_nutritions()
        self.save_data()
