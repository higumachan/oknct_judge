from flask import *
import functools
import hashlib
import urllib

def require_login(func):
    @functools.wraps(func)
    def wrapeer(*args, **kwargs):
        if (session.has_key("username") == True and session.has_key("passwd") == True):
            user = g.db.users.find_one({"username": session["username"]});
            if (user == None):
                return ("Invalid User");
            kwargs["user"] = user;
        else:
            path = request.path;
            get_request = urllib.urlencode({
                "redirect": path
            });
            return (redirect("/login?" + get_request));

        return func(*args, **kwargs);
    return wrapeer;

def user_login(username, passwd):
    session["username"] = username;
    session["passwd"] = hashlib.sha1(passwd).digest().encode("base64");

def user_logout():
    session.pop("username");
    session.pop("passwd");

def user_create(username, passwd):
    passwd_hash = hashlib.sha1(passwd).digest().encode("base64");
    new_id = g.db.users.count();
    user = g.db.users.find_one({"username": username});
    if (user == None):
        user = {"_id": new_id, "username": username, "passwd": passwd_hash}
        g.db.users.insert(user);
        return (user);
    return (None);

