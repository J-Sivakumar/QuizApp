from flask import *
import sqlite3
import requests
import random
import html 
from flask_mail import *

app = Flask(__name__)
app.secret_key= 'siva'   


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html') 

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/success', methods=['POST'])
def success():
    msg = "Invalid email/password"
    try:          
        with sqlite3.connect('users.db') as con:
            cursor = con.cursor()
            cursor.execute('Select * from user where email ="'+request.form['email']+'"')
            data = cursor.fetchall()
            
            if data:
                if data[0][1]==request.form['pwd']:
                    msg = 'Login successfully'
                    if request.method =='POST':
                        session['emailid'] = request.form['email']
                    if 'emailid' in session:
                        return render_template('success.html',name=data[0][2])
                    
                else:
                    msg = "Invalid email/password"
            
            
    except BaseException as e:
        msg =e
        con.rollback()
    finally:
        con.close()
    return render_template('login.html',msg=msg)
    

@app.route('/success1', methods=['POST'])
def success1():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['name']
        password = request.form['pwd']
        password1 = request.form['pwd1']

        if password!=password1:
            msg = "Password Does not match"
            return render_template('register.html',form = request.form,msg = msg)
        else:

            try:
                
                with sqlite3.connect('users.db') as con:
                    cursor = con.cursor()
                    cursor.execute('Insert into user (email,password,username) values(?,?,?)',(email,password,username))
                    con.commit()
                    msg = 'Registered successfully'
            except:
                con.rollback()
                msg = 'User already exists Please Login Here'
                return render_template('login.html',msg = msg)
            finally:
                con.close()
            return render_template('success1.html',msg = msg)

@app.route('/changepwd')
def change():
    return render_template("updatepwd.html")

@app.route('/success2',methods=['POST'])
def update():
    if request.method =='POST':
        email = request.form['email']
        pwd = request.form['pwd']
        try:      
            with sqlite3.connect('users.db') as con:
                cursor = con.cursor()
                cursor.execute('Update user set password = "'+pwd+'" where email ="'+email+'"')
                con.commit()
                cursor.execute('Select email,password from user where email ="'+request.form['email']+'"')
                data = cursor.fetchall()
            
                if data:
                    if data[0][1]==request.form['pwd']:
                        msg = 'Updated successfully'                    
                else:
                     msg = 'Invalid Email/Failed to Update'
        except BaseException as e:
                con.rollback()
                msg =e
        finally:
                con.close()
                return msg
    return "Failed to Update"

@app.route('/profile')
def profile():
    if 'emailid' in session:
        try:      
            with sqlite3.connect('users.db') as con:
                cursor = con.cursor()
                cursor.execute('Select * from user where email ="'+session['emailid']+'"')
                data = cursor.fetchall()
                if data:
                        return render_template('profile.html',data = data[0])  
        except BaseException as e:
            con.rollback()
        finally:
                con.close()
        return 'An error Occured'
    else:
         abort(401)

@app.route('/logout')
def logout():
    if 'emailid' in session:
        session.pop('emailid',None)
        return render_template('logout.html')
    return "You are already logout"

@app.route('/quiz')
def quiz():
    return render_template('quizinfo.html')
dict={} 
@app.route('/result',methods=['post','get'])
def result():
    ans=0
    for i in range(len(dict)):
        if  str(i) in request.form and dict[i]['correct']==request.form[str(i)]:
            ans+=1
    ans = str(ans) + "/" + str(len(dict))
    return render_template('result.html',ans = ans, dict=dict , len= len(dict))

@app.route('/playquiz',methods=['post','get'])
def playquiz():
    if request.form['Level'] != 'any':
        response = requests.get("https://opentdb.com/api.php?amount="+request.form['amt']+"&category=18&difficulty="+request.form['Level']+"&type=multiple")
    else:
        response = requests.get("https://opentdb.com/api.php?amount="+request.form['amt'] +"&category=18&type=multiple")
    que = response.json()['results']
    for i in range(len(que)):
        options = [que[i]['correct_answer']] + que[i]['incorrect_answers']
        for  j in range(len(options)):
            options[j] = html.unescape(options[j])
        random.shuffle(options)
        dict[i]={'question':html.unescape(que[i]['question']),'option':options, "correct":que[i]['correct_answer']}
    return render_template('question.html', dict = dict, len= len(dict))

if __name__=='__main__':
    app.run(debug = True)


