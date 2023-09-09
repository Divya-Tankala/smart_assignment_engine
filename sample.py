# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 22:45:21 2023

@author: Laharika
"""

from flask import Flask, render_template, request,session


app=Flask(__name__)

@app.route('/')

def welcome():
    return render_template("facultystulist.html")

@app.route('/facultymarks')

def greet():
    return render_template("facultymarks.html")
if __name__=='__main__':
    app.run(debug=True)