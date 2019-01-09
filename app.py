from flask import Flask,render_template
from data import Article

app = Flask(__name__)

article = Article()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html',articles = article)

@app.route('/article/<string:id>/')
def get_article(id):
    return render_template('article.html',id=id)

if __name__ == '__main__':
    app.run(debug=True)