from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import os


with open("/Users/akashmahato/Documents/Python_Coding/codeBlog_flask/config.json", "r") as c:
    params = json.load(c)["params"]
#local_server = True
app = Flask(__name__)

app.config.update(MAIL_SERVER = "smtp.googlemail.com",
                MAIL_PORT = 587,
                MAIL_USE_TLS = True,
                MAIL_USERNAME =params['recipient_mail'],
                MAIL_PASSWORD=params['recipient_password'])     #for gmail server

mail = Mail(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:@localhost/TechnoHub"  #'mysql://root:@localhost/TechnoHub'
app.secret_key = params['secret-key']

# if local_server == True:
#     app.config['SQLALCHEMY_DATABASE_URI'] = params["local_server_uri"]
# else:
#     app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

db = SQLAlchemy(app)

class Contacts(db.Model):
#    sno ,name,email,phone_num,msg,date ---->as copied from the database
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12),nullable=False)
    msg = db.Column(db.String(120), nullable=True)
    date = db.Column(db.String(12), nullable=True)


class Posts(db.Model):
#    sno ,title,content,date ---->as copied from the database
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=True)
    slug = db.Column(db.String(80), nullable=True)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    

@app.route('/')
def home():
    posts = Posts().query.filter_by().all()[0:]
    return render_template("index.html",params=params,posts=posts)


@app.route("/about")
def about():
    return render_template("about.html",params=params)


@app.route('/dashboard',methods=["GET","POST"])
def login():
    if 'user' in session and session['user'] == params['login_username']:
        posts = Posts.query.all()
        return render_template("dashboard.html",params=params, posts=posts)
    if request.method == 'POST':
        #Goto Admin Panel
        uname = request.form.get("username")
        pwd = request.form.get("pwd")
        if uname == params['login_username'] and pwd == params['login_password']:
            #Set the Session Variable
            session['user'] = uname
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
       
    else:
        return render_template("login.html",params=params)


@app.route('/logout')
def logout():
    session.pop('user', None)
    # flash('You were logged out')
    return redirect('/dashboard')
    

@app.route('/edit/<string:sno>', methods=["GET","POST"])
def edit_post(sno):
    if 'user' in session and session['user'] == params['login_username']:
        
        if request.method == 'POST':
            new_slug = request.form.get('slug')
            new_title = request.form.get('title')
            new_content = request.form.get('content')
            new_img_file = request.form.get('img_file')
            new_tagline = request.form.get('tagline')
            new_date = datetime.now()
            if sno == '0':
                #Adding a new post
                post = Posts(slug=new_slug, title=new_title, content=new_content, img_file=new_img_file, tagline=new_tagline, date=new_date)
                db.session.add(post)
                db.session.commit()
            else:
                #Editing the existing post
                post = Posts().query.filter_by(sno=sno).first()
                post.slug = new_slug
                post.title = new_title
                post.content = new_content
                post.img_file = new_img_file
                post.tagline = new_tagline
                post.date = new_date
                db.session.commit()
                redirect("/edit"+sno)
        post = Posts().query.filter_by(sno=sno).first()
        return render_template("edit_posts.html",params=params, sno = sno, post=post)

@app.route('/delete/<string:sno>', methods=["GET","POST"])
def delete_post(sno):
    if 'user' in session and session['user'] == params['login_username']:
        post = Posts().query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect("/dashboard")





@app.route('/uploader',methods=["GET","POST"])
def file_uploader():
    if 'user' in session and session['user'] == params['login_username']:
        received_file = request.files['file1']
        received_file.save(os.path.join(params['uploaded_file_path'], secure_filename(received_file.filename)))
        return "File Uploaded successfully"


@app.route("/contact",methods = ["GET","POST"])
def contact():
    if request.method == "POST":
        """Add entry to the database"""
        person_name = request.form.get("name")   #these variables are as per the names in contact.html
        email_id = request.form.get("email_id")
        phone_number = request.form.get("phone_number")
        message = request.form.get("message")
        

        #    sno ,name,email,phone_num,msg,date ---->as copied from the database
        database_entry = Contacts(name = person_name, email = email_id, phone_num = phone_number, date=datetime.now(), msg = message)
        db.session.add(database_entry)
        db.session.commit()
        

        mail.send_message(f"New message from {person_name}",
                      sender=email_id,
                      recipients=[params['recipient_mail']],
                      body=message)
        return render_template("contact.html",params=params)




@app.route("/post/<string:post_slug>",methods = ['GET'])
def samplepost(post_slug):
    post = Posts(date=datetime.now())
    post = post.query.filter_by(slug = post_slug).first()
    return render_template("post.html",params=params,post=post)





if __name__ == "__main__":
    app.run(debug=True)
