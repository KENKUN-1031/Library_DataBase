# coding: utf-8
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm.exc import UnmappedInstanceError

app = Flask(__name__, static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.todo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.static_folder = 'static'

db = SQLAlchemy(app)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(128), nullable=True)#name
    book = db.Column(db.String(128), nullable=True)#bookname
    time = db.Column(db.String(128), nullable=True)#time borrowed
    returned = db.Column(db.Boolean, nullable=False, default=False)#if the book is returned or not
    returned_time = db.Column(db.String(128), nullable=False, default="N/A")#the time when book was returned
    search_name = db.Column(db.String(128), nullable=True)#the name of person when you search data
    search_book = db.Column(db.String(128), nullable=True)#the name of the book when you search data
    tags = db.Column(db.String(128), nullable=True)#tags


@app.route('/')
def index():
    search_mode = request.args.get("mode")
    if search_mode == "search":
        search_name = request.args.get('search_name')
        search_book = request.args.get('search_book')
        if search_name == "":
            data2 = db.session.query(ToDo).filter(ToDo.book == search_book).all()
            data3 = db.session.query(ToDo).filter(ToDo.book.like("%"+search_book+"%")).all()
        else:
            data2 = db.session.query(ToDo).filter(ToDo.todo == search_name).all()
            data3 = db.session.query(ToDo).filter(ToDo.todo.like("%"+search_name+"%")).all()

        data = data2 + data3
        for i in data2:
            for n in data3:
                if i == n:
                    data.remove(n)
        data.reverse()
    else:
        data = ToDo.query.all()

    return render_template('todo.html', data=data)



@app.route('/test')
def alert():
    data = ToDo.query.all()
    return render_template('todo.html', e = "the data you want to delete doesn't exist", data=data)

@app.route('/alo')
def alert3():
    data = ToDo.query.all()
    return render_template('todo.html', e = "please input the all the information that is needed", data=data)

@app.route('/new')
def alert2():
    data = ToDo.query.all()
    return render_template('todo.html', e="the data you want to add already exists", data=data)

@app.route('/wa')
def alert4():
    data = ToDo.query.all()
    return render_template('todo.html', e="that book is already returned", data=data)




#追加するときのプログラム(add)
@app.route('/add', methods=['POST'])
def add():
    todo = request.form['todo']
    book = request.form['book']
#ここでstockのif文でチェックボックスの中身を確認している
    if todo !="" and book != "":
        number = 0
        returned = False
        first_time = datetime.now()
        returned_t="N/A"
        time = first_time.strftime('%Y/%m/%d %H:%M:%S')
        num = 0
        second = ToDo.query.filter(ToDo.book == book).all()
        if second == []:
            new_todo = ToDo(todo=todo, book=book, time=time, returned=returned, returned_time=returned_t)
            db.session.add(new_todo)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            for i in second:
                if todo == i.todo and book == i.book:
                    return redirect(url_for('alert2'))
                else:
                    num = 1#数字直せ！
                number = number + 1

            if num == 1:
                new_todo = ToDo(todo=todo, book=book, time=time, returned=returned, returned_time=returned_t)
                db.session.add(new_todo)
                db.session.commit()
                return redirect(url_for('index'))
    else:
        return redirect(url_for('alert3'))



#データを変更する(update)
#本を返した場合(when someone returned the book)
@app.route('/update', methods=['POST'])
def update():
    returned_name = request.form['return']
    returned_book = request.form['return_book']
    # del_data = ToDo.query.filter_by(todo=delete_name).first()
    #変更するデータの大元を取得
    returned_log = ToDo.query.filter_by(todo=returned_name, book=returned_book).first()
    #取得した大元のデータの変更する部分のみを取得
    returned_check = returned_log.returned
    first_time = datetime.now()
    time = first_time.strftime('%Y/%m/%d %H:%M:%S')
    #もうすでにreturnされてるかどうかのチェック
    if returned_check == False:
        return_log = True
        if returned_book != "" and returned_name != "":
            try:
                #一行下のプログラムはどのデータを変更するか取得してる
                del_data = ToDo.query.filter_by(todo=returned_name, book=returned_book).first()
                #二行下まででデータを変更してる
                del_data.returned = return_log
                del_data.returned_time = time
                #一行下でプログラムをコミットしてる
                db.session.commit()
                return redirect(url_for('index'))
            except UnmappedInstanceError:
                return redirect(url_for('alert'))
        else:
            return redirect(url_for('alert3'))
    else :
        return redirect(url_for('alert4'))



#消すときのプログラム(delete)
@app.route('/delete',methods=['POST'])
def delete():
    delete_name = request.form['delete']
    delete_book = request.form['delete_book']
    if delete_name != "" and delete_book != "":
        try:
            del_data = ToDo.query.filter_by(todo = delete_name, book=delete_book).first()
            print(del_data)
            db.session.delete(del_data)
            db.session.commit()
            return redirect(url_for('index'))
        except UnmappedInstanceError:
            return redirect(url_for('alert'))
    else:
        return redirect(url_for('alert3'))






if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)




