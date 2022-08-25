from flask import session
import pandas as pd
import sqlite3
import traceback
import sys


def encryption_encode(data):
    #encrypted_data  = fernet.encrypt(data.encode())
    #return encrypted_data
    return data

def encryption_decode(encrypted):
    #data = fernet.decrypt(encrypted).decode()
    #return data
    return encrypted


def create_db():
    """ If there is no any table in database, it creates a user table """
    # connect to database
    conn = sqlite3.connect("recsys.db")

    # create a cursor
    c = conn.cursor()
    try:
        c.execute("""SELECT name FROM sqlite_master WHERE type = 'table'""")
        conn.commit()
        items = c.fetchone()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    if items == None:
        try:
            # create a table
            c.execute("""
            CREATE TABLE users(
                first_name text, 
                last_name text,
                email text, 
                password text,
                weight integer, 
                height integer, 
                age integer, 
                gender integer, 
                activity_level text, 
                undesired_ingredients text, 
                disease text,
                idx_liked text,
                idx_disliked text,
                answers text
            )
            """)
            conn.commit()
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))

    # close connection
    conn.close()

def clear_data(name):
    """
    Clears information of given users

    Parameters
    ----------
    name: str
        first name of user
    """
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()

    try:
        data = ("", "", name)
        c.execute("""
                    UPDATE users 
                    SET idx_liked = ?,
                    idx_disliked = ?
                    WHERE first_name = ?
                  """, data)
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    conn.close()

def survey_control(name):
    """
    Controls whether the given users have completed the survey or not

    Parameters
    ----------
    name: str
        first name of user

    Returns
    -------
    bool
        completed the survey or not
    """
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()

    try:
        c.execute(""" SELECT answers FROM users WHERE first_name = ? """, (name,))
        conn.commit()
        item = c.fetchall()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
    conn.close()
    return len(item) > 0

def get_data(email, password):
    """
    Get data from user whose given mail and password

    Parameters
    ----------
    email: str
        email of user
    password: str
        password of user

    Returns
    ----------
    str, str, str, str, str, str, str,
        weight, height, age, gender, level, undesired_ingredients, disease
    """
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()
    try:
        c.execute("""
               SELECT *
               FROM users 
               WHERE email = ? AND
               password = ?
               """, (encryption_encode(email), encryption_encode(password)))

        data = c.fetchall()
        weight = data[0][4]
        height = data[0][5]
        age = data[0][6]
        gender = data[0][7]
        level = data[0][8]
        undesired_ingredients = data[0][9]
        disease = data[0][10]
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
    conn.close()

    return encryption_decode(weight), encryption_decode(height), encryption_decode(age), encryption_decode(gender), encryption_decode(level), encryption_decode(undesired_ingredients), encryption_decode(disease)

def login(email, password):
    """
    Checks whether a user exist with given email and password

    Parameters
    ----------
    email: str
        email of user
    password: str
        password of user

    Returns
    ----------
    bool
        the user exist or not
    """
    session["email"] = email
    session["password"] = password

    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()
    try:
        c.execute("""
                   SELECT *
                   FROM users 
                   WHERE email = ? AND
                   password = ?
                   """, (encryption_encode(email), encryption_encode(password)))

        data = c.fetchall()
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    conn.close()
    return data != []

def register(first_name, last_name, e_mail, password):
    """
    Registers user to database with the given information

    Parameters
    ----------
    first_name: str
        name of user
    last_name: str
        surname of user
    e_mail: str
        email of user
    password: str
        password of user
    """
    session["first_name"] = first_name
    session["email"] = e_mail
    session["password"] = password
    none_ = None

    data = (encryption_encode(first_name), encryption_encode(last_name),
            encryption_encode(e_mail), encryption_encode(password),
            none_, none_, none_, none_, none_, none_,none_,none_, none_, none_)
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", data)
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    conn.close()

def register_update(weight, height, age, gender, level, undesired_ingredients, disease):
    """
    Updates the information of current user in the system

    Parameters
    ----------
    weight: str
        weight of user
    height: str
        height of user
    age: str
        age of user
    gender: str
        gender of user
    level: str
        activity level of user
    undesired_ingredients: str
        undesired ingredients list of user in string format separated with '#' symbol
    disease: str
        disease name of user if exist
    """
    mail = session["email"]

    session["weight"] = weight

    undesired_ingredients_str = ""
    for ing in undesired_ingredients:
        undesired_ingredients_str += ing + "#"

    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()

    try:
        c.execute("SELECT rowid FROM users WHERE email = ?", (encryption_encode(mail),))
        items = c.fetchone()
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    id   = items[0]
    data = (encryption_encode(weight), encryption_encode(height), encryption_encode(age),
            encryption_encode(gender), encryption_encode(level), encryption_encode(undesired_ingredients_str[:-1]),
            encryption_encode(disease), encryption_encode(id))
    try:
        c.execute("""
                    UPDATE users 
                    SET weight = ?,
                    height = ?,
                    age = ?,
                    gender = ?,
                    activity_level = ?,
                    undesired_ingredients = ? ,
                    disease = ?
                    WHERE rowid = ?
            """, data)

        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    conn.close()

def get_name(mail):
    """ Gets the name of user who currently use the system """
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()
    try:
        c.execute("""SELECT first_name FROM users WHERE email = ?""", (mail,))
        item = c.fetchall()
        first_name = item[0][0]
        session["first_name"] = first_name
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    conn.close()

    return encryption_decode(first_name)

def update_recipe_label(mail, liked, disliked):
    """
    Updates the like and dislike information for given user

    Parameters
    ----------
    mail: str
        e-mail of user
    liked: str
        index sequence of liked items
    disliked: str
        index sequence of disliked items
    """
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()
    try:
        c.execute("SELECT rowid, idx_liked, idx_disliked FROM users WHERE email = ?", (encryption_encode(mail),))
        items = c.fetchone()
        id = encryption_decode(items[0])
        old_liked = encryption_decode(items[1])
        old_disliked = encryption_decode(items[2])
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    if old_liked != None and old_disliked != None:
        liked = encryption_encode(old_liked + "#" + liked)
        disliked = encryption_encode(old_disliked + "#" + disliked)

    try:
        c.execute("""UPDATE users 
                    SET idx_liked = ?, 
                    idx_disliked = ? 
                    WHERE rowid = ?""",
                  (liked, disliked, encryption_encode(id)))
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    conn.close()

def is_name_exist(name):
    """
    Controls whether a user is existed with the given name or not

    Parameters
    ----------
    name: str
        first name of user
    """
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()
    try:
        c.execute("SELECT first_name FROM users")
        items = c.fetchall()
        names = [i[0] for i in items]
        for i in names:
            if encryption_encode(name) in names:
                return True
        return False
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
    conn.close()

def get_weight(first_name):
    """
    Gets the weight of given user

    Parameters
    ----------
    first_name: str
        first name of user
    """
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()
    try:
        c.execute("""SELECT weight FROM users WHERE first_name = ?""", (encryption_encode(first_name),))
        item = c.fetchall()
        weight = "#"
        if item != []:
            if item[0][0] != None:
                weight = encryption_decode(item[0][0])
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
    conn.close()
    return weight

def name_control():
    """ Control if any first name is existed in the session """
    first_name = "#"
    if "first_name" in session:
        first_name_temp = session["first_name"]
        if is_name_exist(first_name_temp):
            first_name = first_name_temp

    return first_name

def weight_control():
    """ Control if the weight information is taken from the current user """
    first_name = name_control()
    weight = get_weight(first_name)
    return weight

def log_out():
    """ Log out from the account """
    session.clear()

def drop_table():
    """  Drops the users table from database """
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()
    try:
        c.execute("DROP TABLE users")
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    conn.close()

def save_answers(q1, q2, q3, q4, name):
    """
    Gets the survey answers of users and save them

    Parameters
    ----------
    q1: str
        answers of question 1
    q2: str
        answers of question 2
    q3: str
        answers of question 3
    q4: str
        answers of question 4
    name: str
        first name of the user
    """
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()
    try:
        c.execute("SELECT rowid FROM users WHERE first_name = ?", (encryption_encode(name),))
        items = c.fetchone()
        id = encryption_decode(items[0])
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    results = (q1 + "#" + q2 + "#" + q3 + "#" + q4)

    try:
        c.execute("""UPDATE users 
                     SET answers = ?
                     WHERE rowid = ?""",
                  (encryption_encode(results), encryption_encode(id)))
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    conn.close()

def stats(answer_list):
    """
    Prints the detailed results of survey

    Parameters
    ----------
    answer_list: list
        survey results
    Returns
    -------
    str
        survey results
    """
    survey_dict = {}
    survey_dict["q1"] = [i[0] for i in answer_list]
    survey_dict["q2"] = [i[1] for i in answer_list]
    survey_dict["q3"] = [i[2] for i in answer_list]
    survey_dict["q4"] = [i[3] for i in answer_list]

    ans_q1s = pd.DataFrame(survey_dict["q1"])
    ans_q2s = pd.DataFrame(survey_dict["q2"])
    ans_q3s = pd.DataFrame(survey_dict["q3"])
    ans_q4s = pd.DataFrame(survey_dict["q4"])

    results = f"""
    *********************************+
    Number of users: {len(answer_list)}+
    +
    Question 1+
    {str(ans_q1s.value_counts()).split("dtype")[0].replace("    ", "->")}+
    ----------------+
    Question 2+
    {str(ans_q2s.value_counts()).split("dtype")[0].replace("    ", "->")}+
    ----------------+
    Question 3+
    {str(ans_q3s.value_counts()).split("dtype")[0].replace("    ", "->")}+
    ----------------+
    Question 4+
    {str(ans_q4s.value_counts()).split("dtype")[0].replace("    ", "->")}+
    *********************************
    """
    return results

def statistics_answers():
    """ Shows the statistics results of survey """
    conn = sqlite3.connect("recsys.db")
    c = conn.cursor()
    try:
        c.execute("""SELECT weight, height, age, gender, activity_level, disease, answers 
                     FROM users
                     WHERE length(answers) > 1
                  """)
        items = c.fetchall()
        if len(items) > 0:
            items_answer = [i[6] for i in items]
            items_ages   = [i[2] for i in items]
            items_gender = [i[3] for i in items]
            items_level  = [i[4] for i in items]
            items_disease= [i[5] for i in items if i[5] != "no"]
            n_men        = len([i for i in items_gender if i == "male"])
            n_female     = len([i for i in items_gender if i == "female"])
            dict_levels = {}
            for i in items_level:
                if i not in dict_levels.keys():
                    dict_levels[i] = 1
                else:
                    dict_levels[i] = dict_levels[i] + 1
            mode_level = [k for k, v in dict_levels.items() if v == max(dict_levels.values())]
            mode_level = mode_level[0]
            age_min = min(items_ages)
            age_max = max(items_ages)
            n_disease = len(items_disease)
            items_weight_mean = 0
            items_height_mean = 0
            for i in items:
                items_weight_mean += i[0]
                items_height_mean += i[1]
            items_weight_mean = items_weight_mean / len(items)
            items_height_mean = items_height_mean / len(items)
        else:
            items_answer = ""
            items_weight_mean = 0
            items_height_mean = 0
            age_min = 0
            age_max = 0
            n_men = 0
            n_female = 0
            n_disease = 0
            mode_level = 0
        conn.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    if len(items_answer) != 0:
        answer_list = [i.split("#") for i in items_answer if i[0] != None]
        survey_results =  stats(answer_list)
        survey_results = survey_results.split("+")
    else:
        survey_results = " "

    session["results"] = {"items_weight_mean": items_weight_mean,
                          "items_height_mean": items_height_mean,
                          "age_min": age_min,
                          "age_max": age_max,
                          "n_men": n_men,
                          "n_female": n_female,
                          "n_disease": n_disease,
                          "mode_level": mode_level,
                          "survey_results": survey_results}
    conn.close()