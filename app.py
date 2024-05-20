from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector



app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'gupta@1'
app.config['MYSQL_DB'] = 'project'
mysql = MySQL(app)




@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = '  '
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `accounts` WHERE username = %s AND password = %s', (username, password,))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			msg = 'Logged in successfully !'
			return render_template('index.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)





@app.route('/output')
def output():
	msg=' '
	return render_template('output.html',msg = msg)





@app.route('/stroke', methods =['GET', 'POST'])
def stroke():
	msg = ' '
	if request.method == 'POST' and 'gender' in request.form and 'age' in request.form and 'hypertension' in request.form and 'heart_disease' in request.form and 'ever_married' in request.form and 'work_type' in request.form and 'residence_type' in request.form and 'avg_glucose_level' in request.form and 'bmi' in request.form and 'smoking_status' in request.form:
		gender = request.form['gender']
		age = request.form['age']
		hypertension = request.form['hypertension']
		heart_disease = request.form['heart_disease']
		ever_married = request.form['ever_married']
		work_type = request.form['work_type']
		residence_type = request.form['residence_type']
		avg_glucose_level = request.form['avg_glucose_level']
		bmi = request.form['bmi']
		smoking_status = request.form['smoking_status']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		if not gender or not age or not hypertension or not heart_disease or not work_type or not residence_type or not ever_married or not avg_glucose_level or not bmi or not smoking_status:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO account_stroke VALUES (NULL, %s,%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,NULL)', (session['username'],gender,age,hypertension,heart_disease,ever_married,work_type,residence_type,avg_glucose_level,bmi,smoking_status, ))
			mysql.connection.commit()
			msg=strokeml(gender,age,hypertension,heart_disease,ever_married,work_type,residence_type,avg_glucose_level,bmi,smoking_status)
			return render_template('output.html', msg = msg)
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('stroke.html', msg = msg)

def strokeml(gender, age, hypertension, heart_disease, ever_married, work_type, residence_type, avg_glucose_level, bmi, smoking_status):
	heart_data = pd.read_csv("Stroke.csv",sep=",")

	heart_data['bmi'].fillna(heart_data['bmi'].median(),inplace=True)

	heart_data.drop('id',axis=1,inplace=True)

	heart_data.gender[heart_data.gender=='Male']=0
	heart_data.gender[heart_data.gender=='Female']=1
	heart_data.ever_married[heart_data.ever_married=='Yes']=1
	heart_data.ever_married[heart_data.ever_married=='No']=0
	heart_data.work_type[heart_data.work_type=='Private']=0
	heart_data.work_type[heart_data.work_type=='Self-employed']=1
	heart_data.work_type[heart_data.work_type=='children']=2
	heart_data.work_type[heart_data.work_type=='Govt_job']=3
	heart_data.work_type[heart_data.work_type=='Never_worked']=4
	heart_data.Residence_type[heart_data.Residence_type=='Urban']=0
	heart_data.Residence_type[heart_data.Residence_type=='Rural']=1
	heart_data.smoking_status[heart_data.smoking_status=='formerly smoked']=0
	heart_data.smoking_status[heart_data.smoking_status=='never smoked']=1
	heart_data.smoking_status[heart_data.smoking_status=='smokes']=2
	heart_data.smoking_status[heart_data.smoking_status=='Unknown']=3

	S= heart_data[heart_data.stroke == 0]
	NS= heart_data[heart_data.stroke == 1]

	S_sample=S.sample(n=251)

	nds=pd.concat([S_sample,NS],axis=0)

	nds['stroke'].value_counts()

	X=nds.drop(columns='stroke',axis=1)
	Y=nds['stroke']

	X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, stratify=Y, random_state=99)

	model = LogisticRegression()

	model.fit(X_train, Y_train)
	gender = float(gender)
	age = float(age)
	hypertension = float(hypertension)
	heart_disease = float(heart_disease)
	ever_married = float(ever_married)
	work_type = float(work_type)
	residence_type = float(residence_type)
	avg_glucose_level = float(avg_glucose_level)
	bmi = float(bmi)
	smoking_status = float(smoking_status)
	input_data=(gender,age,hypertension,heart_disease,ever_married,work_type,residence_type,avg_glucose_level,bmi,smoking_status)	

	input_data_as_numpy_array= np.asarray(input_data)
	input_data_reshaped = input_data_as_numpy_array.reshape(1,-1)
	prediction = model.predict(input_data_reshaped)
	if (prediction[0]== 0):
		return "Congratulations!\n\nYour demographics, lifestyle and body parameters suggest that you’re NOT AT RISK. Spread the will for a health-friendly lifestyle that you follow now and get yourself checked periodically from us or a professional.\n\nCheers!"
	else:
		return "Your demographics, lifestyle and body parameters suggest that you’re AT RISK. Visit a General Physician or a Neurologist near you to confirm, and secure your health and future!\n Adopt a healthier lifestyle and get your family checked as well, as stroke may also be hereditary.\n\nHealth is wealth indeed."








@app.route('/diabetes', methods =['GET', 'POST'])
def diabetes():
	msg = ''
	if request.method == 'POST' and 'pregnancies' in request.form and 'glucose' in request.form and 'bloodpressure' in request.form and 'skinthickness' in request.form and 'insulin' in request.form and 'bmi_dia' in request.form and 'diabetes_pedigree_fnc' in request.form and 'age_dia' in request.form:
		pregnancies = request.form['pregnancies']
		glucose = request.form['glucose']
		bloodpressure = request.form['bloodpressure']
		skinthickness = request.form['skinthickness']
		insulin = request.form['insulin']
		bmi_dia = request.form['bmi_dia']
		diabetes_pedigree_fnc = request.form['diabetes_pedigree_fnc']
		age_dia = request.form['age_dia']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		if not pregnancies or not glucose or not bloodpressure or not skinthickness or not insulin or not bmi_dia or not diabetes_pedigree_fnc or not age_dia:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO account_dia VALUES (NULL, %s, %s, %s, %s,%s,%s,%s,%s,%s,NULL)', (session['username'],pregnancies,glucose,bloodpressure,skinthickness,insulin,bmi_dia,diabetes_pedigree_fnc,age_dia, ))
			mysql.connection.commit()
			msg=diaml(pregnancies,glucose,bloodpressure,skinthickness,insulin,bmi_dia,diabetes_pedigree_fnc,age_dia)
			return render_template('output.html', msg = msg)
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('diabetes.html', msg = msg)

def diaml(pregnancies,glucose,bloodpressure,skinthickness,insulin,bmi_dia,diabetes_pedigree_fnc,age_dia):
	db =pd.read_csv("db.csv",sep=",")

	S= db[db.Outcome == 0]
	NS= db[db.Outcome == 1]
	S_sample=S.sample(n=232)
	nds=pd.concat([S,NS],axis=0)

	X=nds.drop(columns='Outcome',axis=1)
	Y=nds['Outcome']

	X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, stratify=Y, random_state=0)

	model = LogisticRegression()

	model.fit(X_train, Y_train)

	input_data = (float(pregnancies), float(glucose), float(bloodpressure), float(skinthickness), float(insulin), float(bmi_dia), float(diabetes_pedigree_fnc), float(age_dia))	
	input_data_as_numpy_array= np.asarray(input_data)

	input_data_reshaped = input_data_as_numpy_array.reshape(1,-1)

	prediction = model.predict(input_data_reshaped)

	if (prediction[0]== 0):
		return "Congratulations!\n\nYour demographics, lifestyle, and body parameters suggest that you’re NOT AT RISK. Spread the will for a health-friendly lifestyle that you follow now and get yourself checked periodically from us or a professional.\n\nCheers!"
	else:
		return "Your demographics, lifestyle and body parameters suggest that you’re AT RISK. Visit a General Physician or an Endocrinologist near you to confirm, and secure your health and future!\nAdopt a healthier lifestyle by moving more often and get your family checked as well, as diabetes is hereditary.\nHealth is wealth indeed."






@app.route('/cardiovascular', methods =['GET', 'POST'])
def cardiovascular():
	msg = ''
	if request.method == 'POST' and 'age1' in request.form and 'gender1' in request.form and 'height' in request.form and 'weight' in request.form and 'ap_hi' in request.form and 'ap_lo' in request.form and 'cholesterol' in request.form and 'glu' in request.form and 'smoke' in request.form and 'alco' in request.form and 'active' in request.form:
		age1 = request.form['age1']
		gender1 = request.form['gender1']
		height = request.form['height']
		weight = request.form['weight']
		ap_hi = request.form['ap_hi']
		ap_lo = request.form['ap_lo']
		cholesterol = request.form['cholesterol']
		glu = request.form['glu']
		smoke = request.form['smoke']
		alco = request.form['alco']
		active = request.form['active']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		if not age1 or not gender1 or not height or not weight or not ap_hi or not ap_lo or not cholesterol or not glu or not smoke or not alco or not active:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO account_cardiovascular VALUES (NULL, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,NULL)', (session['username'],age1,gender1,height,weight,ap_hi,ap_lo,cholesterol,glu,smoke,alco,active,))
			mysql.connection.commit()
			msg=cardiovascularml(age1,gender1,height,weight,ap_hi,ap_lo,cholesterol,glu,smoke,alco,active)
			return render_template('output.html', msg = msg)
	elif request.method == 'POST':
		msg = 'Please fill out the form2!'
	return render_template('cardiovascular.html', msg = msg)

def cardiovascularml(age1,gender1,height,weight,ap_hi,ap_lo,cholesterol,glu,smoke,alco,active):
	heart_data = pd.read_csv("cardiov.csv",sep=";")
	S= heart_data[heart_data.CARDIO_DISEASE == 0]
	NS= heart_data[heart_data.CARDIO_DISEASE == 1]

	nds=pd.concat([S,NS],axis=0)

	nds['CARDIO_DISEASE'].value_counts()

	X=nds.drop(columns='CARDIO_DISEASE',axis=1)
	Y=nds['CARDIO_DISEASE']

	X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, stratify=Y, random_state=0)

	model = LogisticRegression()

	model.fit(X_train, Y_train)
	
	input_data = (float(age1), float(gender1), float(height), float(weight), float(ap_hi), float(ap_lo), float(cholesterol), float(glu), float(smoke), float(alco), float(active))
	# change the input data to a numpy array
	input_data_as_numpy_array= np.asarray(input_data)

	# reshape the numpy array as we are predicting for only on instance
	input_data_reshaped = input_data_as_numpy_array.reshape(1,-1)
	prediction = model.predict(input_data_reshaped)

	if (prediction[0]== 0):
		return "Congratulations!\n\nYour demographics, lifestyle, and body parameters suggest that you’re NOT AT RISK of cardiovascular diseases.Spread the will for a health-friendly lifestyle that you follow now and get yourself checked periodically from us or a professional.\n\nCheers!"
	else:
		return "Your demographics, lifestyle, and body parameters suggest that you’re AT RISK of one or many of the cardiovascular diseases ( Coronary heart disease, Cardiac arrest, Heart failure etc)\nVisit a General Physician or a Cardiologist near you to confirm, and secure your health and future! Adopt a healthier lifestyle and clean eating habits, and get your family checked as well, as these diseases can be hereditary. \nHealth is wealth indeed."







@app.route('/calculate_bmi', methods=['GET', 'POST'])
def calculate_bmi():
	msg = 'BMI CALCULATOR'
	if request.method == 'POST' and 'weight' in request.form and 'height' in request.form:
		weight = request.form['weight']
		height = request.form['height']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

		if not weight or not height:
			msg = 'Please fill out the form!'
		else:
			weight = float(weight)
			height = float(height)
			
			bmi = calculate_bmi_value(weight, height)
			msg = f'Your BMI is: {bmi}'
			cursor.execute('INSERT INTO account_bmi VALUES (NULL, %s, %s,%s,%s)' ,(session['username'],weight,height, bmi,))
			mysql.connection.commit()
			return render_template('output.html', msg = msg)
	return render_template('calculate_bmi.html', msg=msg)

def calculate_bmi_value(weight, height):
    height_in_meters = height / 100  
    bmi = weight / (height_in_meters ** 2)
    return round(bmi, 2)	   





@app.route('/calculate_calories', methods=['GET', 'POST'])
def calculate_calories():
	msg = 'CALORIE CALCULATOR'
	if request.method == 'POST' and 'gender' in request.form and 'weight' in request.form and 'height' in request.form and 'age' in request.form and 'activity_level' in request.form:
		gender = request.form['gender']
		weight = request.form['weight']
		height = request.form['height']
		age = request.form['age']
		activity_level = request.form['activity_level']

		if not gender or not weight or not height or not age or not activity_level:
			msg = 'Please fill out the form!'
		else:
			weight = float(weight)
			height = float(height)
			age = int(age)
			bmr = calculate_bmr(gender, weight, height, age)
			calorie_msg = calculate_calories_based_on_activity(bmr, activity_level)
			msg = f'Your BMR is: {bmr} calories. {calorie_msg}'
			return render_template('output.html', msg = msg)
	return render_template('calculate_calories.html', msg=msg)

def calculate_bmr(gender, weight, height, age):
    if gender.lower() == 'female':
        bmr = (weight * 10) + (height * 6.25) - (age * 5) - 161
    else:
        bmr = (weight * 10) + (height * 6.25) - (age * 5) + 5
    return int(bmr)

def calculate_calories_based_on_activity(bmr, activity_level):
    activity_levels = {
        'sedentary': 1.2,
        'exercise_1_3': 1.375,
        'exercise_4_5': 1.55,
        'daily_exercise': 1.725,
        'intense_exercise': 1.9,
        'very_intense_exercise': 2.095,
    }
    calorie_multiplier = activity_levels.get(activity_level, 1.2)
    calories = int(bmr * calorie_multiplier)
    return f'Based on your activity level, you need approximately {calories} calories per day.'




 
@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/details')
def details():
    return render_template('details.html')


@app.route('/stroke_info')
def stroke_info():
    return render_template('stroke_info.html')

@app.route('/diabetes_info')
def diabetes_info():
    return render_template('diabetes_info.html')

@app.route('/cardiovascular_info')
def cardiovascular_info():
    return render_template('cardiovascular_info.html')

@app.route('/index')
def index():
	return render_template('index.html')




@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `accounts` WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)





if __name__ == '__main__':
    app.run(debug=True)

