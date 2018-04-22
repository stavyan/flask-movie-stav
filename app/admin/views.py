# coding:utf8
from flask import render_template, redirect, url_for

from . import admin


@admin.route("/")
def index():
    return render_template("admin/index.html")



@admin.route("/login/")
def login():
    return render_template("admin/login.html")



@admin.route("/logout/")
def logout():
    return redirect(url_for("admin.login"))
