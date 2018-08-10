#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/6 14:41
# @Author  : Derek.S
# @Site    : 
# @File    : app.py

from flask import Flask
from flask_bootstrap import Bootstrap
from jinja2.ext import do
from jinja2 import Environment
from flask_wtf.csrf import CSRFProtect
from flask_jsglue import JSGlue
from flask_pymongo import PyMongo
from config import SECRET_KEY, dbConfig


app = Flask(__name__, template_folder="templates")
app.secret_key = SECRET_KEY

app.config.update(
    MONGO_URI=dbConfig["URI"]
)


jsglue = JSGlue(app)
mongo = PyMongo(app)

app.jinja_env.add_extension("jinja2.ext.do")
app.jinja_env.auto_reload = True
bootstrap = Bootstrap(app)
CSRFProtect(app)

