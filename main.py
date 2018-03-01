import sqlite3, os, hashlib, random
from flask import Flask, flash, jsonify, url_for, redirect, render_template, render_template_string, request, session, g
from forms import SearchForm
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
import datetime
import os


app = Flask(__name__)
Bootstrap(app)
app.database = "quiz.db"
app.config['SECRET_KEY'] = 'thekey'#os.urandom(20)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)

disallowed_chars = []

@app.route('/')
@app.route('/index')
def index():
    form = SearchForm(csrf_enabled=False)
    return render_template('index.html', form=form)

@app.route('/profile')
def profile():
    print(session)
    if 'username' not in session:
        flash('Please login')
        return redirect(url_for('index'))
    return render_template('profile.html')

#@app.route('/admin')
#def admin():
#    if 'username' not in session: 


#API routes
@app.route('/api/login', methods=['POST'])
def loginAPI():
    if request.method == 'POST':
        uname, pword = (request.json['username'], request.json['password'])
        g.db = connect_db()
        cur = g.db.execute("SELECT password FROM users WHERE username = '%s'" %(uname,))
        stored_pw = cur.fetchone()
        if stored_pw:
            if check_pass(stored_pw[0], pword):
                result = {'status': 'success'}
                session['username'] = uname
                session['garbage'] = 13844774
                session.permanant = True
                print(session)
            else:
                result = {'status': 'fail'}
        else:
            result = {'status': 'fail'}
        g.db.close()
        return jsonify(result)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/api/search/<item>', methods=['GET'])
def searchAPI(item):
    g.db = connect_db()
    data = []
    try:
        curs = g.db.execute("SELECT quiz_name FROM Quizzes WHERE quiz_name LIKE '%%%s%%'" %item)
        data = [dict(name=row[0]) for row in curs.fetchall()]
    except sqlite3.OperationalError:
        data = [{"name": "Invalid search term"}]
    g.db.close()

    return jsonify(data)

@app.errorhandler(404)
def page_not_found_error(error):
    template = '''{%% extends "bootstrap/base.html" %%}
{%% block body %%}
    <div class="center-content error">
        <h1>Oops! That page doesn't exist.</h1>
        <h3>%s</h3>
    </div>
{%% endblock %%}
''' % (request.url)
    return render_template_string(template), 404

@app.errorhandler(500)
def internal_server_error(error):
    template = '''{%% extends "bootstrap/base.html" %%}
{%% block body %%}
    <div class="center-content error">
        <h1>Seriously...stop making problems.</h1>
    </div>
{%% endblock %%}
'''
    return render_template_string(template), 500

def connect_db():
    return sqlite3.connect(app.database)

# Check entry password against stored hash
def check_pass(stored_pw, entry_pw):
    stored_hash, salt = stored_pw.split(':')
    entry_hash = hash_pass(entry_pw, salt)
    if entry_hash == stored_pw:
        return True
    return False 

# Create password hashes
def hash_pass(pw, salt=None):
    if not salt:
        salt = str(random.SystemRandom().getrandbits(8))
    salted_pw = (pw + salt).encode('utf-8')
    m = hashlib.sha256()
    m.update(salted_pw)
    return "{}:{}".format(m.hexdigest(), salt)

def sanitize(input):
    for x in disallowed_chars:
        input = input.replace(x, "")
    return input

if __name__ == "__main__":

    #create database if it doesn't exist yet
    if not os.path.exists(app.database):
        with sqlite3.connect(app.database) as connection:
            c = connection.cursor()

            c.execute("""CREATE TABLE IF NOT EXISTS `hasTaken` (
                `u_id`	integer NOT NULL,
                `q_id`	integer NOT NULL,
                `score`	text NOT NULL,
                `taken_on`	datetime NOT NULL,
                FOREIGN KEY(`u_id`) REFERENCES `Users`(`id`) ON DELETE CASCADE,
                FOREIGN KEY(`q_id`) REFERENCES `Quizzes`(`q_id`) ON DELETE CASCADE
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS `enrolledIn` (
                `u_id`	integer NOT NULL,
                `c_id`	integer NOT NULL,
                FOREIGN KEY(`c_id`) REFERENCES `Courses`(`c_id`) ON DELETE CASCADE,
                FOREIGN KEY(`u_id`) REFERENCES `Users`(`id`) ON DELETE CASCADE
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS `Users` (
                `id`	integer NOT NULL,
                `first_name`	text,
                `last_name`	text,
                `email`	text NOT NULL,
                `username`	text NOT NULL,
                `password`	text NOT NULL,
                `created`	datetime NOT NULL,
                `last_login`	datetime,
                PRIMARY KEY(`id`)
            )""")
            c.execute("""INSERT INTO `Users` (id,first_name,last_name,username,email,password,created,last_login) VALUES (1,'George','Orwell','goreswell','gorwell@wherever.net','7bf291424921dae56da906b65737bff97715824b21e82a4ea6cd41375245cedc:28','',''),
            (2,'Bob','Geldof','floyd','bobby@lemon.com','33b1731da2a1c9fe6de3a08228e1236d5daea25db3f8a7b90e5d00f7ce5bf0d7:143','',''),
            (3,'Mako','Iwamatsu','mako','mako@nihon.net','e102f3a10201611662b84ea17b56f26adc4ad92afa5174bf718f3221f4432207:6','',''),
            (4,'Tonya','Harding','kneecaps','clubber@fail.org','9e088b2b686dc9b7cfc23629ccc971c3661a6e5e156ac29b780b68712a7b572e:72','',''),
            (5,'Laura','Branigan','nightcreature','taken@above.net','7e736333ba133b4ba5b7ef2c1c4c071c0074dd3f9738284bd4e3334ffbed6121:215','',''),
            (6,'Art','Bell','wildcard','artbell@mindspring.com','b8c926955a6da51faae90de49eea553ff87450fbefad949066519ec0e18f7052:70','',''),
            (7,'Terrence','McKenna','dmtman','hce@levity.com','4dcedacaea5859a4ec3c92dc33dd1450b38a0a099e9555a3a8ecbb5776de9f81:123','',''),
            (8,'BJ','Penn','grndnpnd','bjpenn@fight.org','3154b3ae9ed23d7bcd06c342ad95211fad2d457c80bd26b7be1767ac8babb98f:20','',''),
            (9,'Anderson','Silva','brknleg','aslva@fight.org','819c0ee30c8f8d9e076ff13573b308839b0f6554d0b3ede2170253e3b0b27d39:102','',''),
            (10,'Mike','Judge','pcloadltr','shamir@innatech.com','2a86e2dcd1b4aa66dcaf1ce77bd05521a96f2bd1b340cf9d1654f9808dbc0d18:25','',''),
            (11,'Edmond','Dantes','revenge','ed@chateaudif.net','9c162ab5d3bd2fec11fe57ede1b1a099d9e87f73b144d56404c23ae859db3ebb:108','',''),
            (12,'Maynard','Keenan','toolshed','maynard@undertow.net','54afc913205dd4f42fba36e29660eed52c2ef24c56f3afc8984570e4d2f1c8c7:115','',''),
            (13,'Winston','Wolf','prblmslvr','idrvfast@whatever.com','b09432cf4fa7d311612e47f9acd1eecf77ed5792d5b458aeabce104916f8ad8d:193','',''),
            (14,'Jules','Winnfield','ezekiel2517','shepherd@arf.net','a0a7cdb46844a7a61b0905527cc77683fe06fdd0074975474641019218cc2319:240','',''),
            (15,'Vincent','Vega','royalewithcheese','vegan@orly.com','da51d43d9d654cd1c7bdb06e831fbbdd01731bc64c7e3c9f8d4c7f1e85234e79:96','','')""")
            c.execute("""CREATE TABLE IF NOT EXISTS `Quizzes` (
                `q_id`	INTEGER NOT NULL,
                `c_id`	integer NOT NULL,
                `quiz_name`	text NOT NULL,
                FOREIGN KEY(`c_id`) REFERENCES `Courses`(`c_id`) ON DELETE CASCADE,
                PRIMARY KEY(`q_id`)
            ) WITHOUT ROWID""")
            c.execute("""INSERT INTO `Quizzes` (q_id,c_id,quiz_name) VALUES (1,9,'Network Security Quiz 1'),
            (2,9,'Network Security Quiz 2'),
            (3,9,'Network Security Quiz 3'),
            (4,30,'Machine Learning Quiz 1'),
            (5,30,'Machine Learning Quiz 2'),
            (6,30,'Machine Learning Quiz 3'),
            (7,23,'Mobile Security Quiz 1'),
            (8,23,'Mobile Security Quiz 2'),
            (9,23,'Mobile Security Quiz 3'),
            (10,6,'C++ Quiz 1'),
            (11,6,'C++ Quiz 2'),
            (12,6,'C++ Quiz 3'),
            (13,27,'Artificial Intelligence Quiz 1'),
            (14,27,'Artificial Intelligence Quiz 2'),
            (15,27,'Artificial Intelligence Quiz 3'),
            (16,24,'Digital Forensics Quiz 1'),
            (17,24,'Digital Forensics Quiz 2'),
            (18,24,'Digital Forensics Quiz 3'),
            (19,25,'Secure Coding Quiz 1'),
            (20,25,'Secure Coding Quiz 2'),
            (21,25,'Secure Coding Quiz 3'),
            (22,11,'Web Design Quiz 1'),
            (23,11,'Web Design Quiz 2'),
            (24,11,'Web Design Quiz 3'),
            (25,16,'Data Mining Quiz 1'),
            (26,16,'Data Mining Quiz 2'),
            (27,16,'Data Mining Quiz 3'),
            (28,12,'Algorithms Quiz 1'),
            (29,12,'Algorithms Quiz 2'),
            (30,12,'Algorithms Quiz 3'),
            (31,4,'Programming Languages Quiz 1'),
            (32,4,'Programming Languages  Quiz 2'),
            (33,4,'Programming Languages  Quiz 3'),
            (34,18,'Operating Systems Quiz 1'),
            (35,18,'Operating Systems  Quiz 2'),
            (36,18,'Operating Systems  Quiz 3'),
            (37,17,'Computer Graphics Quiz 1'),
            (38,17,'Computer Graphics Quiz 2'),
            (39,17,'Computer Graphics Quiz 3'),
            (40,5,'Database Design Quiz 1'),
            (41,5,'Database Design Quiz 2'),
            (42,5,'Database Design Quiz 3'),
            (43,3,'Discrete Structures Quiz 1'),
            (44,3,'Discrete Structures Quiz 2'),
            (45,3,'Discrete Structures Quiz 3'),
            (46,26,'Models of Computation Quiz 1'),
            (47,26,'Models of Computation Quiz 2'),
            (48,26,'Models of Computation Quiz 3'),
            (49,1,'Computer Science 1 Quiz 1'),
            (50,1,'Computer Science 1 Quiz 2'),
            (51,1,'Computer Science 1 Quiz 3'),
            (52,2,'Computer Science 2 Quiz 1'),
            (53,2,'Computer Science 2 Quiz 2'),
            (54,2,'Computer Science 2 Quiz 3'),
            (55,15,'Software Engineering Quiz 1'),
            (56,15,'Software Engineering Quiz 2'),
            (57,15,'Software Engineering Quiz 3'),
            (58,19,'Unix Programming Quiz 1'),
            (59,19,'Unix Programming Quiz 2'),
            (60,19,'Unix Programming Quiz 3'),
            (61,29,'Data Visualization Quiz 1'),
            (62,29,'Data Visualization Quiz 2'),
            (63,29,'Data Visualization Quiz 3')""")

            c.execute("""CREATE TABLE IF NOT EXISTS `Courses` (
                `c_id`	integer NOT NULL,
                `course_number`	text NOT NULL,
                `course_name`	text NOT NULL,
                `description`	text,
                PRIMARY KEY(`c_id`)
            )""")

            c.execute("""INSERT INTO `Courses` (c_id,course_number,course_name,description) VALUES (1,'COMP 1900','CS1: Intro COMP Science','Introductory computer science topics'),
            (2,'COMP 2150','CS2: OOP and Data Structures','Object oriented programming paradigms and data structures'),
            (3,'COMP 2700','Discrete Structures','Introductory finite mathematics'),
            (4,'COMP 3050','Programming Languages','Foundations of programming language design paradigms'),
            (5,'COMP 3115','Database Process and Design','Introduction to relational and nosql databases'),
            (6,'COMP 3150','Programming in C/C++','C and C++ programming'),
            (7,'COMP 3160','Adv Data Struct/Algorithm','Advanced topics in data structures and introductory algorithms'),
            (8,'COMP 3410','Computer Org/Architecture','Foundations of computer design and assembly language'),
            (9,'COMP 3825','Network/Info Assurance','Topics in network security'),
            (10,'COMP 4001','Computer Programming','Computer programming'),
            (11,'COMP 4005','Web Design/Development','Designing web applications'),
            (12,'COMP 4030','Design/Analysis Algorithms','Topics in algorithms'),
            (13,'COMP 4040','Programming Languages','Foundations of programming language design paradigms'),
            (14,'COMP 4041','Intro To Compilers','Introduction to compiler design'),
            (15,'COMP 4081','Software Engineering','Software engineering principles'),
            (16,'COMP 4118','Introduction to Data Mining','Topics in data mining and processing'),
            (17,'COMP 4242','Intro Computer Graphics','Introduction to 2D/3D computer graphics'),
            (18,'COMP 4270','Operating Systems','Foundations of operating system principles'),
            (19,'COMP 4272','System Admin and Unix Prog','Foundations of system administration and programming in Unix environments'),
            (20,'COMP 4302','Web Service/Internet','Designing web services'),
            (21,'COMP 4310','Wireless Mobile Comp','Wireless Mobile Comp'),
            (22,'COMP 4410','Computer Security','Topics in computer security'),
            (23,'COMP 4420','Wireless and Mobile Security','Topics in wireless and mobile devie security'),
            (24,'COMP 4430','Digital Forensics','Digital Forensics'),
            (25,'COMP 4432','Secure Coding and Testing','Secure Coding and Testing'),
            (26,'COMP 4601','Models of Computation','Theory of computation'),
            (27,'COMP 4720','Intro Artificial Intelligence','Introductory topics in artificial intelligence'),
            (28,'COMP 4730','Expert Systems','Expert Systems'),
            (29,'COMP 4731','Data Visualization','Data Visualization'),
            (30,'COMP 4745','Intro to Machine Learning','Intro to Machine Learning'),
            (31,'COMP 4882','Capstone Software Proj','Capstone Software Proj'),
            (32,'COMP 4920','Wireless and Mobile Security','Wireless and Mobile Security')""")
            connection.commit()

    app.run(host='0.0.0.0', port=5000) # runs on machine ip address to make it visible on netowrk
