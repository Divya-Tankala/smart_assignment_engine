# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 14:49:41 2023

@author: admin
"""

from flask import Flask, render_template, request,session
from datetime import datetime
import ibm_db
import ibm_boto3
from ibm_botocore.client import Config,ClientError
import os
import re
import random
import string
import requests

app=Flask(__name__)

if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0")
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=mcy26866;PWD=zFttmWFuyj6DR6aw",'','')
print(conn)
print("connection successful...")

@app.route('/facultyprofile')
def fprofile():
    return render_template('facultyprofile.html')

@app.route('/adminprofile')
def aprofile():
    return render_template('adminprofile.html')

@app.route('/studentprofile')
def sprofile():
    return render_template('studentprofile.html')


@app.route('/login', methods=['POST','GET'])
def loginentered():
    global Userid
    global Username
    msg=''
    if request.method=="POST":
        email=str(request.form['email'])
        print(email)
        password=request.form["password"]
        sql= "SELECT * FROM REGISTER WHERE EMAIL=? and PASSWORD=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session["Loggedin"]= True
            session["id"]=account['EMAIL']
            Userid= account['EMAIL']
            session['email']=account['EMAIL']
            Username= account['USERNAME']
            Name=account['NAME']
            msg="Loggedin Successfully"
            sql="SELECT ROLE FROM REGISTER WHERE EMAIL=?"
            stmt=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,email)
            
            ibm_db.execute(stmt)
            r=ibm_db.fetch_assoc(stmt)
            print(r)
            if r["ROLE"]==1:
                print("STUDENT")
                return render_template("studentprofile.html",msg=msg,user=email,name=Name, role="STUDENT", username=Username, email= email)
            elif r["ROLE"]==2:
                print("FACULTY")
                return render_template("facultyprofile.html",msg=msg,user=email,name=Name, role="FACULTY", username=Username, email= email)
            else:
                print("ADMIN")
                return render_template("adminprofile.html",msg=msg,user=email,name=Name, role="ADMIN", username=Username, email= email)
        else:
            msg="Incorrect email or Password"
            
        return render_template("login.html", msg=msg)
    else:
        return render_template("login.html")
            
        
@app.route("/studentsubmit",methods=['POST','GET'])
def sassignment():
    u= Username.strip()
    subtime=[]
    ma = []
    sql= "SELECT SUBMITTIME, MARKS FROM SUBMIT WHERE STUDENTNAME=?"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,u)
    ibm_db.execute(stmt)
    st=ibm_db.fetch_tuple(stmt)
    while st !=False:
        subtime.append(st[0])
        ma.append(st[1])
        st=ibm_db.fetch_tuple(stmt)
    print(subtime)
    print(ma)
    if request.method== "POST":
        for x in range (1,5):
            x=str(x)
            y=str("file"+x)
            print(type(y))
            f=request.files[y]
            print(f)
            print(f.filename)
            
            if f.filename!='':
                basepath=os.path.dirname(__file__)
                filepath=os.path.join(basepath,'uploads',u+x+".pdf")
                f.save(filepath)
                COS_ENDPOINT ="https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints"
                COS_API_KEY_ID="6DVtRnO6_1_j3ynAxB_DIb-w68ZtDoh1V8baosVmUMwn"
                COS_INSTANCE_CRN="crn:v1:bluemix:public:cloud-object-storage:global:a/87b0f5ee26d041cebdf5ad3f0e2cf311:4bd90f6c-ec64-492f-b9ee-94854c7e1c13::"
                cos=ibm_boto3.client("s3",ibm_api_key_id=COS_API_KEY_ID,ibm_service_instance_id=COS_INSTANCE_CRN,config=Config(signature_version="oauth"),endpoint_url=COS_ENDPOINT)
                cos.upload_file(Filename= filepath,Bucket='caddivya',Key=u+x+".pdf")
                msg="Uploading Succesful"
                ts=datetime.now()
                t=ts.strftime("%Y-%m-%d %H:%M:%S")
                sql1= "SELECT * FROM SUBMIT WHERE STUDENTNAME=? AND ASSIGNMENTNUM=?"
                stmt=ibm_db.prepare(conn,sql1)
                ibm_db.bind_param(stmt,1,u)
                ibm_db.bind_param(stmt,2,x)
                ibm_db.execute(stmt)
                acc=ibm_db.fetch_assoc(stmt)
                print(acc)
                if acc==False:
                    sql= "INSERT INTO SUBMIT (STUDENTNAME, ASSIGNMENTNUM, SUBMITTIME) valuse (?,?,?)"
                    stmt=ibm_db.prepare(conn,sql)
                    ibm_db.bind_param(stmt,1,u)
                    ibm_db.bind_param(stmt,2,x)
                    ibm_db.bind_param(stmt,3,t)
                    ibm_db.execute(stmt)
                else:
                    sql="UPDATE SUBMIT SET SUBMITTIME = ? WHERE STUDENTNAME= ? and ASSIGNMENTNUM=?"
                    stmt=ibm_db.prepare(conn,sql)
                    ibm_db.bind_param(stmt,1,u)
                    ibm_db.bind_param(stmt,2,x)
                    ibm_db.bind_param(stmt,3,t)
                    ibm_db.execute(stmt)
                return render_template('studentsubmit.html', msg=msg, datetime=subtime, marks=ma)
                continue
        return render_template("studentsubmit.html",datetime=subtime, Marks=ma)
                    
@app.route("/facultymarks")
def facultymarks():
    data=[]
    sql="SELECT USERNAME from REGISTER WHERE ROLE=1"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)
    name=ibm_db.fetch_tuple(stmt)
    while name!=False:
        data.append(name)
        name=ibm_db.fetch_tuple(stmt)
    data1=[]
    for i in range(0,len(data)):
        y=data[i][0].strip()
        data1.append(y)
    data1 = set(data1)
    data1 = list(data1)
    print(data1)
    
    return render_template("facultystulist.htnl", names=data1, le=len(data1))

@app.route("/marksassign/<string:stdname>", methods=['POST', 'GET'])
def marksassign(stdname):
    global u
    global g
    global file
    da=[]
    COS_ENDPOINT ="https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints"
    COS_API_KEY_ID="Tn7AjMb0oEY73sNH96pFhQDCwEe-KP8fm94lseeUX6mq"
    COS_INSTANCE_CRN="crn:v1:bluemix:public:cloud-object-storage:global:a/87b0f5ee26d041cebdf5ad3f0e2cf311:4bd90f6c-ec64-492f-b9ee-94854c7e1c13::"
    cos=ibm_boto3.client("s3",ibm_api_key_id=COS_API_KEY_ID,ibm_service_instance_id=COS_INSTANCE_CRN,config=Config(signature_version="oauth"),endpoint_url=COS_ENDPOINT)
    output=cos.list_objects(Bucket="studentassignmentsb")
    output
    l=[]
    for i in range(0,len(output['Contents'])):
        j=output['Contents'][i]['Key']
        l.append(j)
    l
    u=stdname
    print(len(u))
    print(len(l))
    n=[]
    
    for i in range(0,len(l)):
        for j in range(0,len(u)):
            if u[j]==l[i][j]:
                n.append(l[i])
    file=set(n)
    file=list(file)
    print(file)
    print(len(file))
    g=len(file)
    sql= "SELECT SUBMITTIME from SUBMIT WHERE STUDENTNAME=?"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,u)
    ibm_db.execute(stmt)
    m=ibm_db.fetch_tuple(stmt)
    while m!=False:
        da.append(m[0])
        m=ibm_db.fetch_tuple(stmt)
    print(da)
    return render_template("facultymarks.html", file=file, g=g,marks=0,datetime=da)
@app.route("/marksupdate/<string:anum>",methods=['POST','GET'])
def marksupdate(anum):
    ma=[]
    da=[]
    mark=request.form['mark']
    print(mark)
    print(u)
    sql="UPDATE SUBMIT SET MARKS =? WHERE STUDENTNAME=? and ASSIGNMENTNUM =?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,mark)
    ibm_db.bind_param(stmt,2,u)
    ibm_db.bind_param(stmt,3,anum)
    ibm_db.execute(stmt)
    msg= "UPDATED"
    sql="select MARKS, SUBMITTIME from SUBMIT WHERE STUDENTNAME=?"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,u)
    ibm_db.execute(stmt)
    m=ibm_db.fetch_tuple(stmt)
    while m!=False:
        ma.append(m[0])
        da.append(m[1])
        m=ibm_db.fetch_tuple(stmt)
    print(ma)
    print(da)
    return render_template("facultymarks.html", msg=msg, marks=ma, g=g, file=file, datetime=da)

@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return render_template("logout.html")

    
@app.route("/register",methods=['POST','GET'])
def signup():
    msg=''
    if request.method=="POST":
        name=request.form["sname"]
        email=request.form['semail']
        username=request.form['susername']
        role = int(request.form['role'])
        password=''.join(random.choice(string.ascii_letters) for i in range(0,8))
        link="https://gnits.ac.in"
        print(password)
        sql="SELECT * FROM REGISTER WHERE EMAIL= ? "
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg="Already Registered"
            return render_template("adminregister.html", error=True,msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg="Invalid Email Address!"
        else:
            insert_sql="INSERT INTO REGISTER VALUES (?,?,?,?,?)"
            prep_stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,name)
            ibm_db.bind_param(prep_stmt,2,email)
            ibm_db.bind_param(prep_stmt,3,username)
            ibm_db.bind_param(prep_stmt,4,password)
            ibm_db.bind_param(prep_stmt,5,role)
            ibm_db.execute(prep_stmt)
            
            url = "https://rapidprod-sendgrid-v1.p.rapidapi.com/mail/send"
            payload = {
                "personalizations": [
                    {
			"to": [{ "email": email }],
			"subject": "Student Account Details"
		}],
	"from": { "email": "divyatankala@gnits.ac.in" },
	"content": [
		{
			"type": "text/plain",
			"value": """Dear {},\n Welcome to University,
            Here there the details to Login into your student portal link:{}\n
            Your username:{}\n Password: {}\n Thank You""".format(name,link,email,password)
		}]
    }
            headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "052ce1c2e4mshd85266c118afd04p13dab2jsn0df3920c549b",
	"X-RapidAPI-Host": "rapidprod-sendgrid-v1.p.rapidapi.com"
}

            response = requests.request("POST",url, json=payload, headers=headers)
            print(response.text)
            msg="Registration Successful"
    return render_template('adminregister.html', msg=msg)