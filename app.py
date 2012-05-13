import sys
sys.path.append('/home/dotcloud/current')

from flask import *
from threading import Thread
from judge import *
import pymongo
import random
import os
from settings import *
from LoginModule import *
import hashlib
from logging.handlers import *

app = Flask(__name__);
app.secret_key = "A0Zr98j/3yX R~XHH!jmN]LWX/,?RT";

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
)
error_log = os.path.join(app.root_path, 'logs/error.log')
error_file_handler = RotatingFileHandler(
    error_log, maxBytes=100000, backupCount=10
)    
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(formatter)
app.logger.addHandler(error_file_handler)


@app.before_request
def before_request():
    if (DOTCLOUD):
        f = open('/home/dotcloud/environment.json');
        env = json.load(f);
        g.conn = pymongo.Connection(env["DOTCLOUD_DATA_MONGODB_HOST"], int(env["DOTCLOUD_DATA_MONGODB_PORT"]));
        g.conn.admin.authenticate(env['DOTCLOUD_DATA_MONGODB_LOGIN'], env['DOTCLOUD_DATA_MONGODB_PASSWORD']);
    else:
        g.conn = pymongo.Connection();
    g.db = g.conn.ooj; 
    print "request_start";

@app.teardown_request
def teardown_request(exception):
    g.conn.disconnect();
    g.db = None;
    print "request_end"

@app.route("/")
@require_login
def index(user=None):
    return (str(user));

@app.route("/<problem_set>/problems")
def problems(problem_set):
    #res = g.db.problems.find();
    res = g.db.problems.find({"problem_set": problem_set});
    res = list(res)
    for r in res:
        if (r.has_key("title") == False):
            r["title"] = "UnTitle";

    return (render_template("problems.html", problems=res));

@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method == "POST"):
        if (request.args.has_key("redirect") == True):
            redirect_url = request.args["redirect"];
        else:
            redirect_url = "/";
        username = request.form["username"];
        passwd = request.form["passwd"];
        user_login(username, passwd);
        return redirect(redirect_url);
   
    return (render_template("login.html"));

@app.route("/logout", methods=["GET", "POST"])
def logout():
    user_logout();
    return (redirect("/index"));

@app.route("/create", methods=["GET", "POST"])
def regist_user():
    if (request.method == "POST"):
        username = request.form["username"];
        passwd = request.form["passwd"];
        user = user_create(username, passwd);
        return ("/index");
    return (render_template("regist.html"));


@app.route("/submit/<int:problem_id>", methods=["POST", "GET"])
@require_login
def submit(problem_id, user):
    if (request.method == "POST"):
        program = request.form["program"];
        file_name = str(random.randint(0, 1000000));
        file_name = PROGRAMS_PATH + file_name;

        f = open(file_name + ".c", "w");
        f.write(program.encode("utf-8").replace("\xc2\xa5", "\\"));
        f.close();
        
        new_id = g.db.submits.count();
        g.db.submits.insert({"_id": new_id, "status": "None", "problem_id": problem_id, "username": user["username"]});
        thread = Thread(target=judge, args=(file_name, problem_id, new_id));
        thread.start();
        return (redirect("/submits"));
    return (render_template("submit.html"));

@app.route("/submits")
def submits():
    res = g.db.submits.find().sort("_id", pymongo.DESCENDING);

    return (render_template("submits.html", submits=res));

def save_file(file, filename):
    if (file):
        file.save(os.path.join(UPLOAD_PATH, filename));


@app.route("/<problem_set>/add-problem", methods=["GET", "POST"])
@require_login
def add_problem(problem_set, user):
    if (request.method == "POST"):
        title = request.form["title"];
        input_file = request.files["input_file"];
        answer_file = request.files["output_file"];
        
        new_id = g.db.problems.count();
        input_filename = str(new_id) + "_in.txt";
        answer_filename = str(new_id) + "_ans.txt";
        save_file(input_file, input_filename);
        save_file(answer_file, answer_filename);
        g.db.problems.insert({"_id": new_id, "title": title, "problem_set": problem_set, "input_file": input_filename, "answer_file": answer_filename});
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

