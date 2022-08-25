import pandas as pd


class Disease:
    """
     A class to represent avoided ingredients for some diseases

    Attributes
    ----------
    diabetes: list
        list that contains avoid ingredients for diabetes
    heart diseases: list
        list that contains avoid ingredients for heart diseases
    celiac: list
        list that contains avoid ingredients for celiac
    hypertension: list
        list that contains avoid ingredients for hypertension
    cirrhosis: list
        list that contains avoid ingredients for cirrhosis
    kidneys: list
        list that contains avoid ingredients for kidneys
    obesite: list
        list that contains avoid ingredients for obesite
    """
    def __init__(self):
        self.diabetes = ["sugar", "sweet", "fat", "white bread", "rice", "pasta", "fruit yogurt", "flavored coffee", "honey", "agave nectar",
                        "maple syrup", "dried fruit", "saltine crackers", "graham crackers", "pretzels", "Fruit juice", "french fries"]
        self.heart_disease = ["sugar", "fat", "bacon", "red meat", "beef", "lamb", "pork", "soda", "cookies", "cakes", "muffins", "hot dogs",
                              "sausage", "salami", "lunch meat", "rice", "bread", "pasta", "snacks", "pizza", "alcohol", "flavored yogurts",
                              "french fries", "fried chicken", "ice cream"]
        self.celiac = ["wheat", "barley", "rye", "triticale", "farina", "spelt", "kamut", "wheat berries", "farro", "couscous", "white bread",
                       "whole wheat bread", "potato bread", "rye bread", "sourdough bread", "wheat crackers", "whole wheat wraps", "flour tortillas",
                       "flatbread", "bagels", "soy sauce", "barbecue sauce", "salad dressings", "marinades", "cream sauces", "spice blends",
                       "gravy mixes", "malt vinegar", "ketchup", "cakes", "cookies", "pastries", "pretzels", "doughnuts", "muffins", "pancakes",
                       "waffles", "noodles", "spaghetti", "gnocchi", "dumplings", "pretzels", "granola bars", "cereal bars", "chips", "energy bars",
                       "cookies", "snack mixes", "candy bars", "beer", "bottled wine coolers", "premade coffee drinks", "drink mixes",
                       "commercial chocolate milk", "veggie burgers", "hot dogs", "prepared lunch meats", "processed cheeses", "egg substitutes",
                       "canned soups", "soup mixes", "puddings", "instant dessert mixes", "ice creams", "breakfast cereals", "french fries", "fried",
                       "flavored tofu"]
        self.hypertension = ["breads", "rolls", "pizza", "sandwiches", "cold cuts", "cured meats", "soup", "burritos", "tacos", "bread", "cheese",
                             "various condiments", "pickles", "tomato", "sauces", "pasta sauces", "tomato juices", "full fat milk", "cream",
                             "red meat", "chicken skin", "nuts", "seeds", "olive oil", "avocado"]
        self.cirrhosis = ["margarine", "vegetable shortening", "fried foods", "chips", "crackers", "pretzels", "microwave popcorn", "hot dogs", "sausage",
                          "deli meats", "bacon", "beef jerky", "soy sauce", "teriyaki sauce", "steak sauce", "spaghetti sauce", "poultry", "eggs", "fish",
                          "oysters", "mussels", "wine", "beer", "spirits", "cocktails"]
        self.kidneys = ["dried apricots", "bran", "granola", "chocolate", "lentils", "beans", "baked beans", "milk", "yogurt", "molasses", "nuts", "seeds",
                        "peanut butter", "phosphate", "beer", "dark colas", "chocolate candy", "caramels", "chocolate drinks", "cheese", "milk", "ice cream,"
                        "yogurt", "creamy soups", "organ meats", "oysters", "sardines", "fish roe", "processed foods", "pizza", "hot dogs", "bacon",
                        "sausage""whole grain bread", "bran cereals"]
        self.obesite = ["french fries", "potato chips", "sugary drinks", "white bread", "candy bars", "fruit juice", "pastries", "cookies", "cakes", "beer",
                        "ice cream", "pizza"]

def common_ingredients(df, n):
    """
    Finds most n common ingredients in all the items

    Parameters
    ----------
    df: DataFrame
        dataframe that contains all the information
    n: int
        given number for how much items to get

    Returns
    -------
    list
        list for indexes of items for n most common ingredients
    """
    dict_ = {}
    for i in df.ingredients:
        for j in i.split("^"):
            if j not in dict_.keys():
                dict_[j] = 1
            else:
                dict_[j] += 1
    common_ing = pd.DataFrame(data=dict_.values(), index=dict_.keys(), columns=["Count"]).sort_values(by="Count",
                                                                                                      ascending=False)[
                 :n]
    return list(common_ing.index)

def bmr(weight, height, age, gender):
    """
    Calculates the Basal Metabolic Rate (BMR) for given information

    Parameters
    ----------
    weight: int, float
        weight of user
    height: int, float
        height of user
    age: int
        age of user
    gender: str
        gender of user

    Returns
    float
        calculated bmr value
    """
    if gender == "male":
        return round(66.47 + (13.75 * weight) + (5.003 * height) - (6.755 * age), 3)
    elif gender == "female":
        return round(655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age), 3)

def daily_caloric_need(bmr_, dict_, activity_level):
    """
    Calculates the daily calorie need of user by using bmr and activity level

    Parameters
    ----------
    bmr_: float
        bmr value of user
    dict_: dict
        dictionary for activity levels
    activity_level: str
        key names of dict_

    Returns
    -------
    int
        returns daily calorie need of user
    """
    return int(bmr_ * dict_[activity_level])

class filter():
    def __init__(self):
        self.filtered_data_idx = None

    def get_indexes(self, df_, avoid_list):
        index_list = []
        for i, item in df_.iterrows():
            for j in avoid_list:
                if j in item.ingredients:
                    index_list.append(i)
        return index_list

    def drop_from_df(self, df_, indexes):
        return df_.drop(index=indexes)

    def filter_by(self, df, weight, height, age, gender, activity_level, disease, health_aware, und_ingredients, n_common):
        """
        Filter the available items according to the some procedures

        Parameters
        ----------
        df: DataFrame
        weight: int, float
            weight of user
        height: int, float
            height of user
        age: int
            age of user
        gender: str
            gender of user
       activity_level: str
            key names of activity level dict for user
       ingredients: list
            list of ingredients which are undesired for the user
       n_common: int
            number of common ingredients to be considered

        Returns
        -------
        DataFrame
            filtered dataframe
        """

        dict_level = {"Level1": 1.2,
                      "Level2": 1.375,
                      "Level3": 1.46,
                      "Level4": 1.725,
                      "Level5": 1.9}

        dcn = daily_caloric_need(bmr(weight, height, age, gender), dict_level, activity_level)
        calori_limit = (dcn / 3) + ((dcn / 3) * 0.1)

        df_new = df.copy()

        common_ing_names = list(common_ingredients(df, n_common))
        common_ing_names.remove("eggs")
        common_ing_names.remove("water")

        if health_aware != None:
            avoid_nutrition_class = ["fat_class", "cholesterol_class"]
            for nut in avoid_nutrition_class:
                df_new = df_new[df_new[nut] != "high"]
            df_new

        if disease != "No":
            diseases = Disease()
            if disease == "diabetes":
                df_new = self.drop_from_df(df_new, self.get_indexes(df_new, diseases.diabetes))
            elif disease == "heart":
                df_new = self.drop_from_df(df_new, self.get_indexes(df_new, diseases.heart_disease))
            elif disease == "celiac":
                df_new = self.drop_from_df(df_new, self.get_indexes(df_new, diseases.celiac))
            elif disease == "blood_pressure":
                df_new = self.drop_from_df(df_new, self.get_indexes(df_new, diseases.hypertension))
            elif disease == "cirrhosis":
                df_new = self.drop_from_df(df_new, self.get_indexes(df_new, diseases.cirrhosis))
            elif disease == "kidney":
                df_new = self.drop_from_df(df_new, self.get_indexes(df_new, diseases.kidneys))
            elif disease == "obesity":
                df_new = self.drop_from_df(df_new, self.get_indexes(df_new, diseases.obesite))

        ing_response_dict = dict(zip(common_ing_names, und_ingredients))

        for kv in ing_response_dict.items():
            if kv[1] == 1:
                if kv[0] == "egg":
                    df_new = df_new[df_new["eggs"] == 0]
                df_new = df_new[df_new[kv[0]] == 0]
                df_new = self.drop_from_df(df_new, self.get_indexes(df_new, [kv[0]]))

        #print(f"\nWeight: {weight}\nHeight: {height}\nAge: {age}\nActivity level: {activity_level}\nDisease: {disease}\n\nIngredients: {ing_response_dict}")

        df_new = df_new[(df_new.calories <= calori_limit)]
        self.filtered_data_idx = list(df_new.index)
        return df_new
