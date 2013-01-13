#!/usr/bin/env python3
"""User package"""

import __importfix__; __package__ = 'dbapi'
from .__init__ import *
import math
import dbapi.dbtime as dbtime
from dbapi.paragraph import Paragraph as Paragraph
#from dbapi.story import Story
import dbapi.story

def nuke():
    conn.execute("DROP TABLE IF EXISTS users;")


class UsernameAlreadyExists(Exception):
    pass

class User(object):
    def __init__(self, uid, fname, lname, username, password, dob, email, joindate, location, bio, image):
        self.uid = uid
        self.fname = fname
        self.lname = lname
        self.username = username
        self.password = password
        self.dob = dob
        self.email = email
        self.joindate = joindate
        self.location = location
        self.bio = bio
        self.image = image

    @classmethod
    def find(cls, field_name:str, query:str = ""):
        """
        Arguments required, in order: the query (what the user is searching for), and the field name of the field they are searching in.
        """
        cur = conn.cursor()
        if field_name == "all":
            cur.execute("SELECT id, fname, lname, username, password, dob, email, joindate, location, bio, image FROM users")
        else:
            cur.execute("SELECT id, fname, lname, username, password, dob, email, joindate, location, bio, image FROM users WHERE " + field_name + " = ?",
                    (query,))
        rows = cur.fetchall()
        results = []
        for row in rows:
            results.append(User(*row))
        return results
    #When you edit, use User.find()[0] (you can't edit multiple results, it will just edit the first one)

    def create(fname, lname, username, password, year, month, day, email, location, bio, image):
        joindate = dbtime.make_time_str()
        dob = dbtime.make_time_str((year, month, day))
        return User(None, fname, lname, username, password, dob, email, joindate, location, bio, image)
        
    #Don't use update, but don't delete it either!!!
    def update(self, fieldname, value):
        cur = conn.cursor()
        cur.execute("UPDATE users SET "+ fieldname +" = ? WHERE id = ?",
                    (value, self.uid))

    def save(self):
        if self.uid is None:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username = ?",(self.username,))
            rows = cur.fetchall()
            results = []
            for row in rows:
                results.append(User(*row))
            if results:
                raise UsernameAlreadyExists()
            else:
                cur.execute("""INSERT INTO users
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (self.uid, self.fname, self.lname, self.username, self.password, self.dob, self.email, self.joindate, self.location, self.bio, self.image))
                self.uid = cur.lastrowid
        else:
            self.update('fname', self.fname)
            self.update('lname', self.lname)
            self.update('password', self.password)
            self.update('email', self.email)
            self.update('location', self.location)
            self.update('bio', self.bio)
            self.update('image', self.image)
        conn.commit()
        #User name and id can't change

    def delete(self):
        cur = conn.cursor()
        cur.execute('''DELETE FROM users
                    WHERE id = ?''', (self.uid,))
        conn.commit()

    def get_contributed_stories(self):
        cur = conn.cursor()
        cur.execute("""SELECT s.id
            FROM stories s JOIN paragraph p ON s.id = p.story_id JOIN users u ON p.author_id = u.id
            WHERE u.id = ?""",
            (self.uid,))
        rows = cur.fetchall()
        results = []
        for row in rows:
            results += dbapi.story.Story.find("id", *row)
        return results

    def get_stories(self):
        cur = conn.cursor()
        cur.execute("""SELECT s.id
            FROM stories s JOIN users u ON s.author_id = u.id
            WHERE u.id = ?""",
            (self.uid,))
        rows = cur.fetchall()
        results = []
        for row in rows:
            results += dbapi.story.Story.find("id", *row)
        return results
        

if __name__ == "__main__":
    s = User.find('username', 'barry_1233')[0]
    previous_name = s.fname
    if s.fname == "Barry":
        s.fname = "Melissa"
    else:
        s.fname = "Barry"
    s.save()
    s2 = User.find('username', 'barry_1233')[0]
    assert s2.fname != previous_name, "Name didn't change :("        

    stories = s2.get_stories()
    assert len(stories), "Should have some stories"

