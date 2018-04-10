# -*- encoding=UTF-8 -*-

from datamanager import app, db
from models import Image, User, Comment
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
import random, hashlib, json, uuid, os
from flask_login import login_user, logout_user, current_user, login_required
import pymysql
from pyecharts import Pie,Bar,Line,HeatMap
import datetime

@app.route('/')
def index():
    myechart = store_interest()
    loan_sum = get_reg_cnt()
    if current_user.is_authenticated:
        return render_template('index.html', loan_sum = loan_sum, myechart = myechart)
    else:
        return redirect('/regloginpage/')
    #return render_template('index.html') 
   
def redirect_with_msg(target, msg, category):
    if msg != None:
        flash(msg, category=category)
    return redirect(target)

@app.route('/regloginpage/')
def regloginpage():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['reglogin']):
        msg = msg + m
    return render_template('login.html', msg=msg, next=request.values.get('next'))

@app.route('/login/', methods={'post', 'get'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/', u'用户名或密码不能为空', 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user == None:
        return redirect_with_msg('/regloginpage/', u'用户名不存在', 'reglogin')

    m = hashlib.md5()
    m.update(password + user.salt)
    if (m.hexdigest() != user.password):
        return redirect_with_msg('/regloginpage/', u'密码错误', 'reglogin')

    login_user(user)

    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)

    return redirect('/')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

def conn_db():
    conn = pymysql.connect(user='sd_sc01',passwd='sd_sc01',host='rr-bp1x1q15h8955237mo.mysql.rds.aliyuncs.com',charset='utf8',db='xindaishuju')
    return conn

def get_reg_cnt():
    loan_sum = {}
    cursor=conn_db().cursor()
    now = datetime.datetime.now()
    today = now.strftime('%Y%m%d')
    tomorrow = (now + datetime.timedelta(days=1)).strftime('%Y%m%d')
    sql1 = "SELECT count(DISTINCT id) FROM xindaishuju.busy_member_base where create_time BETWEEN UNIX_TIMESTAMP("+today+") AND UNIX_TIMESTAMP("+tomorrow+") - 1 union all SELECT count(DISTINCT userid) FROM xindaishuju.busy_member_accural where create_time BETWEEN UNIX_TIMESTAMP("+today+") AND UNIX_TIMESTAMP("+tomorrow+") - 1 union all select count(DISTINCT userid) from xindaishuju.busy_member_contract where status = 1 and create_time BETWEEN UNIX_TIMESTAMP("+today+") AND UNIX_TIMESTAMP("+tomorrow+") - 1 union all select sum(money) from xindaishuju.busy_member_contract where status = 1 and create_time BETWEEN UNIX_TIMESTAMP("+today+") AND UNIX_TIMESTAMP("+tomorrow+") - 1"
    cursor.execute(sql1)
    sqlresult = cursor.fetchall()
    loan_sum['reg_cnt'] = int(sqlresult[0][0])
    loan_sum['appl_cnt'] = int(sqlresult[1][0])
    loan_sum['cont_cnt'] = int(sqlresult[2][0])
    loan_sum['cont_mon'] = sqlresult[3][0]
    return loan_sum

def get_appl_date():
    cursor=conn_db().cursor()
    sql = 'select FROM_UNIXTIME(create_time,"%Y%m%d") as dt,\
       count(distinct admin_id) sto_cnt,\
       count(DISTINCT userid) appl_cnt,\
       sum(month) as money,\
       round(sum(month)/count(DISTINCT userid),2) as moneyperuid,\
       round(count(DISTINCT userid)/count(distinct admin_id)),\
       round(sum(month)/count(DISTINCT admin_id),2)\
       from xindaishuju.busy_member_accural  GROUP BY dt'
    cursor.execute(sql)
    sqlResults = cursor.fetchall()
    return sqlResults

def appl_money():
    sqlResults = get_appl_date()
    date = []
    appl_money = []
    for sqlResult in sqlResults:
        date.append(sqlResult[0])
        appl_money.append(sqlResult[3])
    line = Line(width='100%', height=500)
    line.add("所有商家",x_axis=date,y_axis=appl_money,yaxis_name='金额',xaxis_name='日期',yaxis_name_pos='end',xaxis_name_pos='end',xaxis_name_gap=35,is_smooth=True,is_datazoom_show=True,datazoom_range=[0,100],mark_line=["max", "average"],is_label_emphasis=True)
    return line.render_embed()

def appl_avarge():
    sqlResults = get_appl_date()
    date = []
    appl_avarge = []
    for sqlResult in sqlResults:
        date.append(sqlResult[0])
        appl_avarge.append(sqlResult[4])
    line = Line(width='100%', height=500)
    line.add("所有用户",x_axis=date,y_axis=appl_avarge,yaxis_name='金额',xaxis_name='日期',yaxis_name_pos='end',xaxis_name_pos='end',xaxis_name_gap=35,is_smooth=True,is_datazoom_show=True,datazoom_range=[0,100],mark_line=["max", "average"],is_label_emphasis=True)
    return line.render_embed()

def appl_avarge_store():
    sqlResults = get_appl_date()
    date = []
    appl_avarge = []
    for sqlResult in sqlResults:
        date.append(sqlResult[0])
        appl_avarge.append(sqlResult[6])
    line = Line(width='100%', height=400)
    line.add("所有用户",date,appl_avarge,is_smooth=True,mark_line=["max", "average"],is_label_emphasis=True)
    return line.render_embed()

def store_interest():
    sql = "SELECT actual_repayment_time,sum(back_Interest) from busy_admin_add_transaction where actual_repayment_time BETWEEN '2017-07-01' AND '2018-04-09' GROUP BY actual_repayment_time"
    cursor=conn_db().cursor()
    cursor.execute(sql)
    sqlResults = cursor.fetchall()
    date = []
    interest = []
    for sqlResult in sqlResults:
        date.append(sqlResult[0])
        interest.append(sqlResult[1])
    line = Line(width='100%', height=400)
    line.add("所有用户",x_axis=date,y_axis=interest,yaxis_name='金额',xaxis_name='日期',yaxis_name_pos='end',xaxis_name_pos='end',xaxis_name_gap=35,is_smooth=True,is_datazoom_show=True,datazoom_range=[0,100],mark_line=["max", "average"],is_label_emphasis=True)
    return line.render_embed()
    


@app.route("/loan_sum/")
def loan_sum():
    myechart=appl_money()
    return render_template('graph.html', myechart=myechart)

@app.route("/avarge/")
def avarge():
    return render_template('graph.html', myechart=appl_avarge())

@app.route("/tables/")
def tables():
    loans = get_appl_date()
    return render_template('tables.html',loans=loans)
