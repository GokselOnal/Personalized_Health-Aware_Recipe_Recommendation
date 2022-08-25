import pandas as pd
import warnings
import json


class PrepStep2():
    """
    A class to represent step2 of preprocessing

    Attributes
    ----------
    df: DataFrame
        DataFrame before the preprocessing operations
    common_ing: list
        list that contains n most common ingredients from all items

    Methods
    ----------
    load_dataset()
        gets dataframe
    text_cleaning(cols)
        convert some string values as integers
    clean()
        applies cleaning operations
    process_calories()
        applies preprocessing operations for calories features
    convert_int()
        converts string values as integers
    get_most_common_ing(n=30)
        gets the n most common ingredients
    process_ingredients()
        applies preprocessing operations for ingredients features
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
        """
        self.df = None
        self.common_ing = None

    def load_data(self):
        """ Gets dataframe """
        self.df = pd.read_csv("../preprossed_data.csv")

    def text_cleaning(self, cols):
        """ Converts '<1' values as 1 """
        if cols == '< 1':
            return 1
        else:
            return cols

    def clean(self):
        """ Applies cleaning operations """
        self.df = self.df.dropna()
        self.df = self.df.reset_index()

        nutritions = ['niacins', 'sugars', 'sodium', 'carbohydrates', 'vitamin_B6', 'calories',
                      'thiamin', 'fat', 'folate', 'calcium', 'cholesterol', 'fiber', 'iron',
                      'magnesium', 'potassium', 'protein', 'saturatedfat','vitaminA', 'vitaminC']

        for col in self.df[nutritions].columns:
            self.df[col] = self.df[col].apply(self.text_cleaning)

        self.df[nutritions] = self.df[nutritions].apply(pd.to_numeric)

    def process_calories(self):
        """ Applies preprocessing operations for calories features """
        warnings.filterwarnings('ignore')

        list_calories = pd.Series([])

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
                if dict_["name"] == "Calories":
                    d = {k: dict_["amount"]}
                    list_calories = list_calories.append(pd.Series(d))
            k += 1
        self.df["calories"] = list_calories
        self.df["calories"] = self.df["calories"].apply(self.text_cleaning)
        self.df["calories"] = self.df["calories"].apply(pd.to_numeric)


    def convert_int(self):
        """ Converts string values as integers """
        def convert_str_to_int(str_):
            if ("m" in str_) and ("h" not in str_) and ("d" not in str_):
                return int(str_.replace(" m",""))
            elif (("h" in str_) or ("m" in str_)) and ("d" not in str_):
                if len(str_) == 3 or len(str_) == 4:
                    return int(str_.split("h")[0]) * 60
                elif len(str_) > 4 and len(str_) < 10:
                    return (int(str_.split("h")[0]) * 60) + int(str_.split("h")[1].split("m")[0])
            elif "d" in str_:
                if len(str_) == 3 or len(str_) == 4:
                    return int(str_.split("d")[0]) * 60 * 24
                elif (len(str_) > 4 and len(str_) < 10) and ("m" in str_):
                    return (int(str_.split("d")[0]) * 60 * 24) + int(str_.split("d")[1].split("m")[0])
                elif (len(str_) > 4 and len(str_) < 10) and ("h" in str_):
                    return (int(str_.split("d")[0]) * 60 * 24) + (int(str_.split("d")[1].split("h")[0]) * 60)
                elif len(str_) >= 11:
                    return (int(str_.split("d")[0]) * 24 * 60) + (int(str_.split("d")[1].split("h")[0]) * 60) + (int(str_.split("d")[1].split("h")[1].split("m")[0]))

        self.df.prep = self.df.prep.apply(convert_str_to_int)
        self.df.cook = self.df.cook.apply(convert_str_to_int)
        self.df.ready_in = self.df.ready_in.apply(convert_str_to_int)

    def get_most_common_ing(self, n=30):
        """ Gets the n most common ingredients """
        dict_ = {}
        for i in self.df.ingredients:
            for j in i.split("^"):
                if j not in dict_.keys():
                    dict_[j] = 1
                else:
                    dict_[j] += 1
        dict_
        self.common_ing = pd.DataFrame(data=dict_.values(), index=dict_.keys(), columns=["Count"]).sort_values(by="Count", ascending=False)[:n]

    def process_ingredients(self):
        """ Applies preprocessing operations for ingredients features """
        warnings.filterwarnings('ignore')
        k = 0
        for i in self.common_ing.index:
            self.df[i] = None
        for i in self.df.ingredients:
            for j in self.common_ing.index:
                if j in i.split("^"):
                    self.df[j].loc[k] = 1
                else:
                    self.df[j].loc[k] = 0
            k += 1

    def save_data(self):
        """ Saves the preprocessed data """
        #self.df.to_csv("../preprossed_data.csv", index=False)

    def ready_df(self):
        """ Applies all other methods in this class in a sequence """
        self.load_data()
        self.clean()
        self.process_calories()
        self.convert_int()
        self.get_most_common_ing()
        self.process_ingredients()
        self.save_data()
