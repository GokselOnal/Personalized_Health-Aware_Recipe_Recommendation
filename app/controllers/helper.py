from flask import request, session
from sklearn.ensemble import RandomForestClassifier
from ..models.recommender import RecommendationModel
from .database import get_name
from cryptography.fernet import Fernet


key = Fernet.generate_key()
fernet = Fernet(key)

def get_personal_data():
    """ Gets personal data from web """
    weight = int(request.form.get("weight"))
    height = int(request.form.get("height"))
    age = int(request.form.get("age"))
    gender = request.form.get("gender")
    level = request.form.get("level")
    undesired_ingredients = request.form.getlist("ingredient")
    disease = request.form.get("disease")
    health_aware = request.form.get("health-aware")
    return weight, height, age, gender, level, undesired_ingredients, disease, health_aware

def fill_empty_data(list, fill_with, n_cluster, n):
    """
    Fills empty values in the given list with given symbol

    Parameters
    ----------
    list: list
        given list
    fill_with: str
        given symbol for empty values
    n_cluster: int
        used to calculate number of empty items
    n: int
        used to calculate number of empty items

    Returns
    -------
    list
        full filled list with given symbol
    """
    if (len(list) < (n_cluster * n)):
        diff = (n_cluster * n) - len(list)
        for i in range(diff):
            list.append(fill_with)
    return list

def create_info_dict(dict_, list_, key):
    """
    Adds item to given dictionary with given key and value
    Parameters
    ----------
    dict_: dict
        given dictionary
    list_: list
        given list for value of an item in dictionary
    prefix: str
        given key for an item of dictionary

    Returns
    -------
    dict
        updated dictionary with new item
    """
    dict_[key] = list_
    return dict_

def labelling_set(asked_idx, idx_label1):
    """
    Gets that all asked items and items which is labelled as 1(liked) and set a dictionary with liked and disliked items

    Parameters
    ----------
    asked_idx: list
        list that contains indexes of asked items
    idx_label1: list
        list that contains indexes of items which is labelled as 1

    Returns
    -------
    dict
        dictionary with asked items and their labels (liked or disliked)
    """
    for i in range(len(idx_label1)):
        idx_label1[i] = int(idx_label1[i])

    d = {}
    for i in range(len(asked_idx)):
        d[asked_idx[i]] = 0

    for i in range(len(asked_idx)):
        if asked_idx[i] in idx_label1:
            d[asked_idx[i]] = 1
        else:
            d[asked_idx[i]] = -1

    if " " in list(d.keys()):
        del(d[" "])

    return d

def labelling_set2(label_1_idx, label_0_idx):
    """ Second varient of method labelling_set """
    d = {}
    for i in label_1_idx + label_0_idx:
        if i in label_1_idx:
            d[i] = 1
        else:
            d[i] = -1
    return d

def get_info(df, indexes_asked_img):
    """
    Get information in the given database

    Parameters
    ----------
    df: DataFrame
        dataframe that contains all information
    indexes_asked_img: list
        a list of indexes that is searched for information

    Returns
    -------
    list
        returns a list that contains many information for given indexes
    """
    nutritions_name = ['niacins', 'sugars', 'sodium', 'carbohydrates', 'vitamin_B6', 'calories', 'thiamin', 'fat', 'folate', 'calcium',
                       'cholesterol', 'fiber', 'iron', 'magnesium', 'potassium','protein', 'saturatedfat', 'vitaminA', 'vitaminC']

    durations_name =['prep', 'cook', 'ready_in']

    indexes_asked_img = list(indexes_asked_img)
    recipe_name       = list(df.loc[indexes_asked_img]["recipe_name"])
    rating            = list(df.loc[indexes_asked_img]["aver_rate"])
    review_nums       = list(df.loc[indexes_asked_img]["review_nums"])
    calorie           = list(df.loc[indexes_asked_img]["calories"])
    rate_star         = list()
    directions        = list(df.loc[indexes_asked_img]["directions"])
    ingredients       = list(df.loc[indexes_asked_img]["ingredients"])


    for i in range(len(rating)):
        dec = (rating[i] * 10) % 10
        if dec >= 5:
            rate_star.append(int((rating[i]*10) / 10) + 1)
        else:
            rate_star.append(int((rating[i]*10) / 10))
        rating[i] = str(rating[i])[0] + "." + str(rating[i])[2]

    for i in range(len(calorie)):
        calorie[i] = round(calorie[i], 2)

    nutritions_vals = []
    for nut in nutritions_name:
        if nut == "calories":
            rounded_calories_list = []
            for i in range(len(list(df.loc[indexes_asked_img][nut]))):
                rounded_calories_list.append(round(calorie[i], 2))
            nutritions_vals.append(rounded_calories_list)
        else:
            nutritions_vals.append(list(df.loc[indexes_asked_img][nut]))

    durations_vals = []
    for dur in durations_name:
        durations_vals.append(list(df.loc[indexes_asked_img][dur]))

    updated_ingredients = []
    for ing in ingredients:
        updated_ingredients.append(ing.replace("^", " | "))

    for i in range(len(directions)):
        directions[i] = directions[i][:-2]

    return_list =  [indexes_asked_img, recipe_name, rating, review_nums, calorie, rate_star, nutritions_vals, durations_vals, directions, updated_ingredients]
    return return_list

def fill_empty_total(img_list, indexes_asked_img, recipe_name, rating, review_nums, calorie, rate_star, nutritions_vals, durations_vals, directions, ingredients, n_cluster, n):
    """
    Applies fill_empty_data method for all given list

    Parameters
    ----------
    img_list: list
        list that contains img_url information
    indexes_asked_img: list
        list that contains indexes of asked items
    recipe_name: list
        list that contains recipe_name information
    rating: list
        list that contains rating information
    review_nums: list
        list that contains review_nums information
    calorie: list
        list that contains calorie information
    rate_star: list
        list that contains rate_star information
    nutritions_vals: list
        list that contains nutritions_vals information
    durations_vals: list
        list that contains durations_vals information
    directions: list
        list that contains directions information
    ingredients: list
        list that contains ingredients information
    n_cluster: int
        used to calculate number of empty items
    n: int
        used to calculate number of empty items

    Returns
    -------
    list
        returns a list that contains lists which filled all the given list with given symbols
    """
    img_list          = fill_empty_data(img_list, " ", n_cluster, n)
    indexes_asked_img = fill_empty_data(indexes_asked_img, " ", n_cluster, n)
    recipe_name       = fill_empty_data(recipe_name, "no-name", n_cluster, n)
    rating            = fill_empty_data(rating, "0", n_cluster, n)
    review_nums       = fill_empty_data(review_nums, "0", n_cluster, n)
    calorie           = fill_empty_data(calorie, "0", n_cluster, n)
    rate_star         = fill_empty_data(rate_star, "0", n_cluster, n)
    directions        = fill_empty_data(directions, " ", n_cluster, n)
    ingredients       = fill_empty_data(ingredients, " | ", n_cluster, n)

    filled_nutritions_vals = []
    for nut_list in nutritions_vals:
        filled_nutritions_vals.append(fill_empty_data(nut_list, "0", n_cluster, n))

    filled_durations_vals = []
    for dur_list in durations_vals:
        filled_durations_vals.append(fill_empty_data(dur_list, "0", n_cluster, n))

    return_list = [img_list, indexes_asked_img, recipe_name, rating, review_nums, calorie, rate_star, filled_nutritions_vals, filled_durations_vals, directions, ingredients]
    return return_list

def create_dict(indexes_asked_img, img_list, recipe_name, rating, review_nums, calorie, rate_star, nutritions_vals, durations_vals, directions, ingredients):
    """
    Applies create_info_dict method for all given list
    Parameters
    ----------
    img_list: list
        list that contains img_url information
    indexes_asked_img: list
        list that contains indexes of asked items
    recipe_name: list
        list that contains recipe_name information
    rating: list
        list that contains rating information
    review_nums: list
        list that contains review_nums information
    calorie: list
        list that contains calorie information
    rate_star: list
        list that contains rate_star information
    nutritions_vals: list
        list that contains nutritions_vals information
    durations_vals: list
        list that contains durations_vals information
    directions: list
        list that contains directions information
    ingredients: list
        list that contains ingredients information

    Returns
    -------
    dict
        returns a dict that contains all the information

    """
    nutritions_name = ['niacins', 'sugars', 'sodium', 'carbohydrates', 'vitamin_B6', 'calories', 'thiamin', 'fat', 'folate', 'calcium',
                       'cholesterol', 'fiber', 'iron', 'magnesium', 'potassium','protein', 'saturatedfat', 'vitaminA', 'vitaminC']

    durations_name = ['prep', 'cook', 'ready_in']

    data = {}
    data = create_info_dict(data, indexes_asked_img, "idx_")
    data = create_info_dict(data, img_list, "item")
    data = create_info_dict(data, recipe_name, "recipename")
    data = create_info_dict(data, rating, "rate")
    data = create_info_dict(data, review_nums, "review")
    data = create_info_dict(data, calorie, "cal")
    data = create_info_dict(data, rate_star, "star")
    data = create_info_dict(data, directions, "direction")
    data = create_info_dict(data, ingredients, "ingredient")

    for i in range(len(nutritions_vals)):
        data = create_info_dict(data, nutritions_vals[i], nutritions_name[i])

    for i in range(len(durations_vals)):
        data = create_info_dict(data, durations_vals[i], durations_name[i])

    return data

def apply_processes(df, index_labeled_data, img_list, n_cluster, n):
    """
    Applies get_info, fill_empty_total, create_dict methods in a sequence in one method

    Parameters
    ----------
    df: DataFrame
        dataframe that contains all information
    index_labeled_data: list
        a list of indexes that has labels
    img_list: list
        list that contains img_url information
    n_cluster: int
        used to calculate number of empty items
    n: int
        used to calculate number of empty items

    Returns
    -------
    dict, list
        returns a dict that contains all the information, a list of indexes that has asked

    """
    return_list_info = get_info(df, index_labeled_data)
    indexes_asked_img, recipe_name, rating, review_nums = return_list_info[0], return_list_info[1], return_list_info[2], return_list_info[3]
    calorie, rate_star, nutritions_vals, durations_vals = return_list_info[4], return_list_info[5], return_list_info[6], return_list_info[7]
    directions, ingredients = return_list_info[8], return_list_info[9]

    return_list = fill_empty_total(img_list, indexes_asked_img, recipe_name, rating, review_nums, calorie, rate_star, nutritions_vals, durations_vals, directions, ingredients, n_cluster, n)
    img_list, indexes_asked_img, recipe_name, rating        = return_list[0], return_list[1], return_list[2], return_list[3]
    review_nums, calorie, rate_star, filled_nutritions_vals = return_list[4], return_list[5], return_list[6],return_list[7]
    filled_durations_vals, directions, ingredients          = return_list[8], return_list[9], return_list[10]

    rate_star = [int(rate) for rate in rate_star]

    data = create_dict(indexes_asked_img, img_list, recipe_name, rating, review_nums, calorie, rate_star, nutritions_vals, durations_vals, directions, ingredients)

    return data, indexes_asked_img

def create_model(technique):
    """ Creates a recommender model with given technique """
    model_ins = RecommendationModel()
    model_ins.create_object(technique=technique,
                            model=RandomForestClassifier(),
                            n_cluster=6,
                            n=1)
    return model_ins

def get_instances(model_):
    """ Returns the instances of given recommender model """
    object = model_.instance
    X, y = model_.X, model_.y
    main_df = model_.dataframe
    model = model_.model
    n_cluster = model_.n_cluster
    n = model_.n
    return object, X, y, main_df, model, n_cluster, n

def get_answers():
    """ Gets answers of user from survey """
    q1 = request.form.get("q1")
    q2 = request.form.get("q2")
    q3 = request.form.get("q3")
    q4 = request.form.get("q4")
    mail = session["email"]
    name = get_name(mail)
    return q1, q2, q3, q4, name
