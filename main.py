import json

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
t=None
key="f341b7ed2a506b061854e08f4a434541"
class editf(FlaskForm):
    rating=StringField("New Rating",validators=[DataRequired("Some input is required")])
    review=StringField("New Review",validators=[DataRequired("Some input is required")])
    submit=SubmitField("Submit")

class editf2(FlaskForm):
    rating=StringField("Rating (between 1 and 10)",validators=[DataRequired("Some input is required")])
    review=StringField("Review",validators=[DataRequired("Some input is required")])
    submit=SubmitField("Submit")


class addf(FlaskForm):
    title=StringField("Movie Name",validators=[DataRequired()])
    submit=SubmitField("Submit")



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///movies_data.db'
db=SQLAlchemy(app)

class Movies(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),unique=True,nullable=False)
    year=db.Column(db.Integer,nullable=False)
    description=db.Column(db.String(100),nullable=True)
    rating=db.Column(db.Integer,nullable=False)
    ranking=db.Column(db.Integer,nullable=False,unique=True)
    review=db.Column(db.String(100),nullable=True)
    image_url=db.Column(db.String(200),nullable=False,unique=True)
db.create_all()



@app.route("/")
def home():
    all_movies=db.session.query(Movies).order_by(Movies.rating.desc()).all()
    ids=[]
    titles=[]
    ratings=[]
    years=[]
    reviews=[]
    descriptions=[]
    rankings=[]
    image_urls=[]
    le=len(all_movies)
    for i in range(len(all_movies)):
        ids.append(all_movies[i].id)
        titles.append(all_movies[i].title)
        ratings.append(all_movies[i].rating)
        rankings.append(all_movies[i].ranking)
        reviews.append(all_movies[i].review)
        years.append(all_movies[i].year)
        descriptions.append(all_movies[i].description)
        image_urls.append(all_movies[i].image_url)
    print(ids)
    return render_template("index.html",ii=ids,l=le,ti=titles,rat=ratings,ran=rankings,ye=years,re=reviews,de=descriptions,im=image_urls)

@app.route("/edit/",methods=["GET","POST"])
def edit():
    form=editf(request.form)
    id_movie = request.args.get('id', default=1, type=int)
    print(id_movie)
    if request.method == 'POST':
        if form.is_submitted():
            newrat=form.rating.data
            newrev=form.review.data
            movie_to_update=Movies.query.get(id_movie)
            movie_to_update.rating=newrat
            movie_to_update.review=newrev
            db.session.commit()
            return home()
    else:
        return render_template("edit.html",form=form)

@app.route("/delete/",methods=["GET","POST"])
def dele():
    id_movie = request.args.get('id', default=1, type=int)
    book_to_delete=Movies.query.get(id_movie)
    db.session.delete(book_to_delete)
    db.session.commit()
    return home()

@app.route("/add/",methods=["GET","POST"])
def ad():
    form=addf(request.form)
    if request.method == 'POST':
        if form.is_submitted():
            global t
            t = form.title.data
            l=[]
            url=f"https://api.themoviedb.org/3/search/movie"
            p={'api_key':'f341b7ed2a506b061854e08f4a434541',
               'query': t,
               'page':1,
               'include_adult': 'false'}
            response=requests.get(url,params=p)
            data=response.json()
            d=data['total_pages']
            try:
                for i in range(d):
                    ye=data['results'][i]['release_date']
                    ti=data['results'][i]['original_title']
                    mo=f"{ti} - {ye}"
                    l.append(mo)
                print(l)
                print(d)

                return render_template("select.html",li=l,len=d,tit=t)
            except:
                pass
    else:
        return render_template("add.html",form=form)



@app.route("/add2/",methods=["GET","POST"])
def add2():
    form=editf2(request.form)
    all_movies = db.session.query(Movies).all()
    lll=len(all_movies)
    id_movie = request.args.get('id', default=1, type=int)
    title_movie = request.args.get('title', default=1, type=str)
    l = []
    print(t)
    url = f"https://api.themoviedb.org/3/search/movie"
    p = {'api_key': 'f341b7ed2a506b061854e08f4a434541',
         'query': title_movie,
         'page': 1,
         'include_adult': 'false'}
    response = requests.get(url, params=p)
    data = response.json()
    d = data['total_pages']
    for i in range(d):
        ye = data['results'][i]['release_date']
        ti = data['results'][i]['original_title']
        mo = f"{ti} - {ye}"
        l.append(mo)
    print(l[id_movie])
    new_ti=data['results'][id_movie]['original_title']
    new_ye=data['results'][id_movie]['release_date'][:4]
    new_de=data['results'][id_movie]['overview']
    new_im=f"https://www.themoviedb.org/t/p/original{data['results'][id_movie]['poster_path']}"
    new_id=lll+1
    new_ran=10-lll

    if request.method == 'POST':
        if form.validate_on_submit():
            new_rat=form.rating.data
            new_rev=form.review.data
            print(new_rat,new_rev,new_ran)
            new_movie = Movies(id=new_id, title=new_ti, year=new_ye,description=new_de,rating=new_rat, ranking=new_ran, review=new_rev,image_url=new_im)
            db.session.add(new_movie)
            db.session.commit()

            return home()
    else:
        return render_template("edit2.html",form=form)
if __name__ == '__main__':
    app.run(debug=True)
