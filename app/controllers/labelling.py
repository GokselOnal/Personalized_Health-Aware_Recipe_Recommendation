from flask import session, request
import pandas as pd
import random
from random import randint as rn
from ..models.RecModels.content_based import ContentBased
from ..models.SiameseNeuralNet.LossCalculation import ContrastiveLoss
from .database import update_recipe_label, clear_data, login, get_data, register_update, get_name
from .helper import get_info, fill_empty_total, create_dict, apply_processes, get_instances, create_model, labelling_set2, get_personal_data
from .personalization import common_ingredients, filter

# recommender
obj, X, y, main_df, model, n_cluster, n = get_instances(create_model("active-learning"))

# Content Based Approach
cb = ContentBased()
cb.load_data()

# Cosine Similarity
sim_matrix = cb.similarity_matrix

# Filter object
filter_obj = filter()

# Loss function
cl = ContrastiveLoss()
cl.load_outputs()
outputs = cl.outputs


def prepare_labelling0(from_):
    """
    Prepares data for filtering operations and first step of labeling

    Parameters
    ----------
    from_: str
        used for where users are redirected here

    Returns 1,0,-1
    -------
    """
    if from_ == "register":
        # get data
        weight, height, age, gender, level, undesired_ingredients, disease, health_aware = get_personal_data()
        register_update(weight,
                        height,
                        age,
                        gender,
                        level,
                        undesired_ingredients,
                        disease)
        prepare_filtering(health_aware)
        return 1
    elif from_ == "login":
        email = request.form.get("e_mail")
        password = request.form.get("password")
        if login(email, password):
            session["first_name"] = get_name(email)
            weight, height, age, gender, level, undesired_ingredients, disease = get_data(email, password)
            if weight == None:
                session["first_name"] = get_name(email)
                return 0
            else:
                session["first_name"] = get_name(email)
                name = get_name(email)
                clear_data(name)
                prepare_filtering(1)
                return 1
        else:
            return -1

def prepare_filtering(health_aware):
    """
    Prepares data for filtering operations

    Parameters
    ----------
    health_aware: bool
        whether user want to get health-aware recommendation or not
    """
    n_common = 30

    common_ing = common_ingredients(main_df, n_common)
    common_ing.remove("eggs")
    common_ing.remove("water")

    weight, height, age, gender, level, undesired_ingredients, disease = get_data(session["email"], session["password"])
    undesired_ingredients_list = undesired_ingredients.split("#")

    dict_ing = {}
    for i in range(len(common_ing)):
        dict_ing[common_ing[i]] = 0

    for ui in undesired_ingredients_list:
        if ui in dict_ing.keys():
            dict_ing[ui] = 1

    filtered_df = filter_obj.filter_by(main_df, weight, height, age, gender, level, disease, health_aware, dict_ing.values(), n_common)
    new_data = obj.get_data2(filtered_df)

    obj.set_X(new_data)

def initial_labelling_get(write_session_labelled_data_name):
    """
    Get in Flask for first labelling step,
    Give users a recipe sample and ask for their favorite recipes among this sample and get the favorite items

    Parameters
    ----------
    write_session_labelled_data_name: str
        saves data in session with this name

    Returns
    -------
    data: dict
        Contains information about the recipe for presenting to user
    """
    dict_ = obj.create_diverse_sample(obj.X, 9, 1)  # {idx: url}
    index_labeled_data = list(dict_.keys())
    img_url_list       = list(dict_.values())

    data, indexes_asked_img = apply_processes(main_df,
                                              index_labeled_data,
                                              img_url_list,
                                              9,
                                              1)
    data["first_name"] = session["first_name"]
    session[write_session_labelled_data_name] = indexes_asked_img
    return data

def initial_labelling_post(session_asked_idx_name, checkbox_name, write_session_labelled_data_name,
                           write_session_idx_y_name, write_session_val_y_name):
    """
    Post in Flask for first labelling step
    Updates the data with the selected favorite recipes from users

    Parameters
    ----------
    session_asked_idx_name: str
        gets data from session with this name
    checkbox_name: str
        gets checked items from the checkbox
    write_session_labelled_data_name: str
        saves data in session with this name
    write_session_idx_y_name: str
        saves data in session with this name
    write_session_val_y_name: str
        saves data in session with this name
    """
    asked_idx = session[session_asked_idx_name]
    label_1_idx = request.form.getlist(checkbox_name)
    session["labelled_by_user"] = label_1_idx

    idx_drop = [i for i in range(len(sim_matrix)) if i not in (filter_obj.filtered_data_idx)]

    if len(sim_matrix.loc[idx_drop]) == len(idx_drop):
        sim_matrix_dropped = sim_matrix.drop(idx_drop, axis=1)
        sim_matrix_dropped = sim_matrix_dropped.drop(idx_drop, axis=0)

    cb.similarity_matrix = sim_matrix_dropped

    series_label1 = pd.Series([])
    series_label0 = pd.Series([])
    for i in label_1_idx:
        series_label1 = pd.concat([series_label1, pd.Series(sim_matrix_dropped.loc[:, int(i)].sort_values(ascending=False)[:100])])
        series_label0 = pd.concat([series_label0, pd.Series(sim_matrix_dropped.loc[:, int(i)].sort_values(ascending=True)[:100])])

    label_1_idx_int = [int(i) for i in label_1_idx]

    label_1_idx = (label_1_idx_int + list(series_label1.index))
    label_0_idx = list(series_label0.index)

    d = labelling_set2(label_1_idx, label_0_idx)

    mail = session["email"]

    str_idx_label1 = ""
    for i in label_1_idx:
        str_idx_label1 += str(i) + "#"

    str_idx_label0 = ""
    for i in label_0_idx:
        str_idx_label0 += str(i) + "#"


    update_recipe_label(mail, str_idx_label1[:-1], str_idx_label0[:-1])

    empty_list = []
    index_labeled_data, y_new = obj.active_learning_updating(empty_list,
                                                             y,
                                                             list(d.keys()),
                                                             list(d.values()))  # it is used for only updating y

    session[write_session_labelled_data_name] = index_labeled_data
    session[write_session_idx_y_name] = list(y_new.index)
    session[write_session_val_y_name] = list(y_new)


def labelling_get(session_labelled_data_name, session_idx_y_name, session_val_y_name,
                  write_session_idx_asked_img_name):
    """
    Get in Flask for labelling steps
    Give users a recipe sample and ask for their favorite recipes among this sample and get the favorite items

    Parameters
    ----------
    session_labelled_data_name: str
        gets data from session with this name
    session_idx_y_name: str
        gets data from session with this name
    session_val_y_name: str
        gets data from session with this name
    write_session_idx_asked_img_name: str
        saves data in session with this name

    Returns
    -------
    data: dict
        Contains information about the recipe for presenting to user
    """
    index_labeled_data = session[session_labelled_data_name]

    y_indx_step1 = session[session_idx_y_name]
    y_val_step1 = session[session_val_y_name]
    y = pd.Series(y_val_step1, y_indx_step1)

    indexes_asked_img = obj.active_learning_labeling(model=model,
                                                     index_labeled_data=index_labeled_data,
                                                     X=obj.X,
                                                     y=y,
                                                     size_uncertain=500,
                                                     n_cluster=n_cluster,
                                                     n=n)

    return_list_info = get_info(main_df, indexes_asked_img)

    img_url_list = obj.images
    indexes_asked_img, recipe_name, rating, review_nums = return_list_info[0], return_list_info[1],  return_list_info[2], return_list_info[3]
    calorie, rate_star, nutritions_vals, durations_vals = return_list_info[4], return_list_info[5], return_list_info[6], return_list_info[7]
    directions, ingredients = return_list_info[8], return_list_info[9]

    return_list = fill_empty_total(img_url_list,
                                          indexes_asked_img,
                                          recipe_name,
                                          rating,
                                          review_nums,
                                          calorie,
                                          rate_star,
                                          nutritions_vals,
                                          durations_vals,
                                          directions,
                                          ingredients,
                                          n_cluster,
                                          n)

    img_list, indexes_asked_img, recipe_name, rating = return_list[0], return_list[1], return_list[2], return_list[3]
    review_nums, calorie, rate_star, filled_nutritions_vals = return_list[4], return_list[5], return_list[6], return_list[7]
    filled_durations_vals, directions, ingredients = return_list[8], return_list[9], return_list[10]

    rate_star = [int(rate) for rate in rate_star]

    data = create_dict(indexes_asked_img,
                              img_list,
                              recipe_name,
                              rating,
                              review_nums,
                              calorie,
                              rate_star,
                              nutritions_vals,
                              durations_vals,
                              directions,
                              ingredients)

    data["first_name"] = session["first_name"]
    session[write_session_idx_asked_img_name] = indexes_asked_img

    return data

def labelling_post(session_asked_idx_name, checkbox_name, session_idx_labelled_data_name, session_idx_y_name, session_val_y_name, write_session_labelled_data_name, write_session_idx_y_name,write_session_val_y_name):
    """
    Post in Flask for labelling steps
    Updates the data with the selected favorite recipes from users

    Parameters
    ----------
    session_asked_idx_name: str
        gets data from session with this name
    checkbox_name: str
        gets checked items from the checkbox
    session_idx_labelled_data_name: str
        gets data from session with this name
    session_idx_y_name: str
        gets data from session with this name
    session_val_y_name: str
        gets data from session with this name
    write_session_labelled_data_name: str
        saves data in session with this name
    write_session_idx_y_name: str
        saves data in session with this name
    write_session_val_y_name: str
        saves data in session with this name
    """
    asked_idx = session[session_asked_idx_name]
    label_1_idx = request.form.getlist(checkbox_name)
    session["labelled_by_user"] = session["labelled_by_user"] + label_1_idx

    sim_matrix = cb.similarity_matrix

    series_label1 = pd.Series([])
    series_label0 = pd.Series([])
    for i in label_1_idx:
        series_label1 = pd.concat([series_label1, pd.Series(sim_matrix.loc[:, int(i)].sort_values(ascending=False)[:100])])
        series_label0 = pd.concat([series_label0, pd.Series(sim_matrix.loc[:, int(i)].sort_values(ascending=True)[:100])])

    label_1_idx_int = [int(i) for i in label_1_idx]

    label_1_idx = (label_1_idx_int + list(series_label1.index))
    label_0_idx = list(series_label0.index)

    d = labelling_set2(label_1_idx, label_0_idx)

    mail = session["email"]

    str_idx_label1 = ""
    for i in label_1_idx:
        str_idx_label1 += str(i) + "#"

    str_idx_label0 = ""
    for i in label_0_idx:
        str_idx_label0 += str(i) + "#"

    update_recipe_label(mail, str_idx_label1[:-1], str_idx_label0[:-1])

    index_labeled_data = session[session_idx_labelled_data_name]

    initial_y_indx = session[session_idx_y_name]
    initial_y_val = session[session_val_y_name]
    y_ = pd.Series(initial_y_val, initial_y_indx)

    index_labeled_data, y_new = obj.active_learning_updating(index_labeled_data,
                                                             y_,
                                                             list(d.keys()),
                                                             list(d.values()))

    session[write_session_labelled_data_name] = index_labeled_data
    session[write_session_idx_y_name] = list(y_new.index)
    session[write_session_val_y_name] = list(y_new)

def scoring():
    """  Finds items for scoring and add them to session for recommendation """
    list_labelled_by_user = session["labelled_by_user"]
    list_labelled_by_user = [int(item) for item in list_labelled_by_user]
    similarity_list = []
    for i in list_labelled_by_user:
        final_mat = cl.similarity_scores(outputs, i)
        similars_idx = cl.most_similars(final_mat, 5)
        similarity_list.append(similars_idx)

    from_img_sim = []
    for i in similarity_list:
        from_img_sim.append(i[rn(0, 4)])

    if len(from_img_sim) >= 5:
        from_img_sim = from_img_sim[:5]

    fitted_model, X_dropped, y_dropped = obj.fit(model, session["labeled_data_step2"], X, y)
    scoring_dict = obj.scoring(fitted_model, X_dropped)
    best_idx = list(scoring_dict.keys())[:200]
    from_active_learning = [best_idx[rn(0, len(best_idx) - 1)] for _ in range(10)]

    recommends = from_active_learning + from_img_sim
    random.shuffle(recommends)
    session["give_recommend"] = recommends

def recommend():
    """
    Gets the information of recipes which will be recommended by the item indexes for recommendation step

    Returns
    -------
    data: dict
        Contains information about the recipe for presenting to user
    """
    idx_recipes = session["give_recommend"]
    return_list_info = get_info(main_df, idx_recipes)
    indexes_asked_img, recipe_name, rating, review_nums = return_list_info[0], return_list_info[1], return_list_info[2], return_list_info[3]
    calorie, rate_star, nutritions_vals, durations_vals = return_list_info[4], return_list_info[5], return_list_info[6], return_list_info[7]
    directions, ingredients = return_list_info[8], return_list_info[9]
    img_url_list = list(main_df.loc[indexes_asked_img]["image_url"])

    return_list = fill_empty_total(img_url_list,
                                   indexes_asked_img,
                                   recipe_name,
                                   rating,
                                   review_nums,
                                   calorie,
                                   rate_star,
                                   nutritions_vals,
                                   durations_vals,
                                   directions,
                                   ingredients,
                                   n_cluster,
                                   n)

    img_list, indexes_asked_img, recipe_name, rating = return_list[0], return_list[1], return_list[2], return_list[3]
    review_nums, calorie, rate_star, filled_nutritions_vals = return_list[4], return_list[5], return_list[6], return_list[7]
    filled_durations_vals, directions, ingredients = return_list[8], return_list[9], return_list[10]

    data = create_dict(indexes_asked_img,
                       img_list,
                       recipe_name,
                       rating,
                       review_nums,
                       calorie,
                       rate_star,
                       nutritions_vals,
                       durations_vals,
                       directions,
                       ingredients)

    data["first_name"] = session["first_name"]
    return data

def sample(n= 200):
    """ Creates a random sample in the data """
    sample = main_df.sample(n)
    return_list_info = get_info(main_df, sample.index)
    indexes_asked_img, recipe_name, rating, review_nums = return_list_info[0], return_list_info[1], return_list_info[2], return_list_info[3]
    calorie, rate_star, nutritions_vals, durations_vals = return_list_info[4], return_list_info[5], return_list_info[6], return_list_info[7]
    directions, ingredients                     = return_list_info[8], return_list_info[9]
    img_url_list = list(main_df.loc[indexes_asked_img]["image_url"])
    data = create_dict(indexes_asked_img, img_url_list, recipe_name, rating, review_nums, calorie, rate_star, nutritions_vals, durations_vals, directions, ingredients)
    return data