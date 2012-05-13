import pymongo
import os
from subprocess import Popen
from settings import *
import time

def file_cmp(a, b):
    a_handle = open(a);
    b_handle = open(b);
    
    a_string = reduce(lambda x, y: x + y, a_handle, "");
    b_string = reduce(lambda x, y: x + y, b_handle, "");
    print "a:" + a_string;
    print "b:" + b_string;

    return (a_string == b_string);

def judge(file_name, problem_id, submit_id):
    db = pymongo.Connection().ooj;
    problem = db.problems.find_one({"_id": problem_id});
    submit = db.submits.find_one({"_id": submit_id});
    
    input_file_handle = open(os.path.join(UPLOAD_PATH, problem["input_file"]));
    answer_file = os.path.join(UPLOAD_PATH, problem["answer_file"]);

    res = os.system("gcc %s -o %s" % (file_name + ".c", file_name + ".out"));
    if (res == 0):
        proc = Popen(args="./%s.out" % file_name, stdin=input_file_handle, stdout=open(file_name + ".txt", "w"));
        proc.poll();
        for i in range(10):
            if (proc.poll() != None):
                break;
            time.sleep(1);
        if (proc.poll() == None):
            proc.kill();
            submit["status"] = "InfinitLoop";
        else:
            print proc.returncode;
            if (proc.returncode != 0):
                submit["status"] = "RuntimeError";
            elif (file_cmp(file_name + ".txt", answer_file) == True):
                submit["status"] = "Accept";
            else:
                submit["status"] = "WA";
    else:
        submit["status"] = "CompileError";

    db.submits.save(submit);

    return (0);

