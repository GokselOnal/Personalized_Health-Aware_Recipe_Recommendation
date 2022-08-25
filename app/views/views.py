from flask import Flask, render_template, redirect, url_for, request, session
from ..controllers import MySessionInterface
from ..controllers import register, create_db, log_out
from ..controllers import prepare_labelling0, initial_labelling_get, initial_labelling_post, labelling_get, labelling_post, scoring, recommend
from ..controllers import sample, drop_table, name_control, weight_control, get_answers, save_answers, statistics_answers,survey_control

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = b"+__+!g0k$3L!+__+"
app.session_interface = MySessionInterface()

#drop_table()


@app.route("/", methods=['POST', 'GET'])
def Index():
    if request.method == 'POST':
        if request.form.get("first_name") == None:
            if prepare_labelling0("login") == 1:
                return redirect(url_for("ActiveLearningStep0"))
            elif prepare_labelling0("login") == -1:
                return redirect(url_for("Invalid"))
            elif prepare_labelling0("login") == 0:
                return redirect(url_for("PersonalData"))
        else:
            #register
            first_name = request.form.get("first_name")
            last_name  = request.form.get("last_name")
            e_mail     = request.form.get("e_mail")
            password   = request.form.get("password")

            register(first_name,
                     last_name,
                     e_mail,
                     password)
            return redirect(url_for("PersonalData"))
    else:
        create_db()
        first_name = name_control()
        weight     =  weight_control()
        statistics_answers()
        return render_template("index.html", first_name=first_name, weight=weight)

@app.route("/story")
def Story():
    first_name = name_control()
    return render_template("about.html", first_name=first_name)

@app.route("/logout", methods=['POST', 'GET'])
def LogOut():
    log_out()
    return redirect(url_for("Index"))

@app.route("/recipes")
def Recipes():
    data = sample()
    first_name = name_control()
    return render_template("recipes.html", **data, first_name=first_name)

@app.route("/contact")
def Contact():
    first_name = name_control()
    return render_template("contact.html", first_name=first_name)

@app.route("/personal-data", methods=['POST', 'GET'])
def PersonalData():
    if request.method == 'POST':
        prepare_labelling0("register")
        return redirect(url_for("ActiveLearningStep0"))
    else:
        first_name = name_control()
        return render_template("personal_data.html", first_name= first_name)

@app.route("/invalid", methods=['POST', 'GET'])
def Invalid():
    return render_template("invalid_account.html")

@app.route("/labelling0", methods=['POST', 'GET'])
def ActiveLearningStep0():
    if request.method == 'POST':
        initial_labelling_post("initial_labeled_idx",
                               "checkbox0",
                               "labeled_data_step0",
                               "initial_y_indx",
                               "initial_y_val")

        return redirect(url_for("ActiveLearningStep1"))
    else:
        data = initial_labelling_get("initial_labeled_idx")
        return render_template("labelling0.html", **data)

@app.route("/labelling1", methods=['POST', 'GET'])
def ActiveLearningStep1():
    if request.method == 'POST':
        labelling_post("ask_data_step1",
                       "checkbox1",
                       "labeled_data_step0",
                       "initial_y_indx",
                       "initial_y_val",
                       "labeled_data_step1",
                       "y_indx_step1",
                       "y_val_step1")
        return redirect(url_for("ActiveLearningStep2"))

    else:
        data = labelling_get("labeled_data_step0",
                             "initial_y_indx",
                             "initial_y_val",
                             "ask_data_step1")

        return render_template("labelling1.html", **data)

@app.route("/labelling2", methods=['POST', 'GET'])
def ActiveLearningStep2():
    if request.method == 'POST':
        labelling_post("ask_data_step2",
                       "checkbox2", 
                       "labeled_data_step1", 
                       "y_indx_step1", 
                       "y_val_step1", 
                       "labeled_data_step2", 
                       "y_indx_step2", 
                       "y_val_step2")
        scoring()
        return redirect(url_for("Recommends"))
    else:
        data = labelling_get("labeled_data_step1",
                             "y_indx_step1", 
                             "y_val_step1", 
                             "ask_data_step2")

        return render_template("labelling2.html", **data)

@app.route("/labelling3", methods=['POST', 'GET'])
def ActiveLearningStep3():
    if request.method == 'POST':
        labelling_post("ask_data_step3",
                "checkboxs3", 
                "labeled_data_step2", 
                "y_indx_step2", 
                "y_val_step2", 
                "labeled_data_step3", 
                "y_indx_step3", 
                "y_val_step3")
        scoring()
        return redirect(url_for("Recommends"))
    else:
        data = labelling_get("labeled_data_step2",
                             "y_indx_step2", 
                             "y_val_step2", 
                             "ask_data_step3")
        return render_template("labelling3.html", **data)

@app.route("/recommendations", methods=['POST', 'GET'])
def Recommends():
    if request.method == 'POST':
        return redirect(url_for("Survey"))
    else:
        data = recommend()
        return render_template("recommended_recipes.html", **data)

@app.route("/survey", methods=['POST', 'GET'])
def Survey():
    if request.method == 'POST':
        q1, q2, q3, q4, name = get_answers()
        save_answers(q1, q2, q3, q4, name)
        return redirect(url_for("Index"))
    else:
        first_name = session["first_name"]
        return render_template("survey.html", first_name=first_name)

@app.route("/survey-results")
def Results():
    results = "***"
    if "results" in session:
        results = session["results"]
    return render_template("survey_results.html", **results)

