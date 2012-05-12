from flask import *
from threading import Thread
from judge import *
import pymongo
import random
import os
from settings import *

app = Flask(__name__);


@app.before_request
def before_request():
    g.conn = pymongo.Connection();
    g.db = g.conn.ooj; 
    print "request_start";

@app.teardown_request
def teardown_request(exception):
    g.conn.disconnect();
    g.db = None;
    print "request_end"

@app.route("/")
def index():
    return ("OK");

@app.route("/submit/<int:problem_id>", methods=["POST", "GET"])
def submit(problem_id):
    if (request.method == "POST"):
        program = request.form["program"];
        file_name = str(random.randint(0, 1000000));
        file_name = PROGRAMS_PATH + file_name;

        f = open(file_name + ".c", "w");
        f.write(program.encode("utf-8").replace("\xc2\xa5", "\\"));
        f.close();
        
        new_id = g.db.submits.count();
        g.db.submits.insert({"_id": new_id, "status": "None", "problem_id": problem_id, "user_id": "hoge"});
        thread = Thread(target=judge, args=(file_name, problem_id, new_id));
        thread.start();
        return ("OK");
    return (render_template("submit.html"));

@app.route("/submits")
def submits():
    res = g.db.submits.find().sort("_id", pymongo.DESCENDING);

    return (render_template("submits.html", submits=res));

def save_file(file, filename):
    if (file):
        file.save(os.path.join(UPLOAD_PATH, filename));


@app.route("/<problem_set>/add-problem", methods=["GET", "POST"])
def add_problem(problem_set):
    if (request.method == "POST"):
        input_file = request.files["input_file"];
        answer_file = request.files["output_file"];
        
        new_id = g.db.problems.count();
        input_filename = str(new_id) + "_in.txt";
        answer_filename = str(new_id) + "_ans.txt";
        save_file(input_file, input_filename);
        save_file(answer_file, answer_filename);
        g.db.problems.insert({"_id": new_id, "problem_set": problem_set, "input_file": input_filename, "answer_file": answer_filename});
        return (redirect(""));

    return (render_template("add_problem.html"));

@app.route("/<problem_set>/show-submit")
def show_submit(problem_set):
    problems = g.db.problems.find({"problem_set": problem_set});
    submits = g.db.submits.find({"problem_id": {"$in": problems}});
    
    return (render_template("show-submit.html", submits=submits));

if __name__ == "__main__":
    app.debug = True;
    app.run();

