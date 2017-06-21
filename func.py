﻿from bottle import request
from urllib import parse
import json
import pymysql
import time
import re
import hashlib

json_data = open('set.json').read()
set_data = json.loads(json_data)

conn = pymysql.connect(host = set_data['host'], user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4')
curs = conn.cursor(pymysql.cursors.DictCursor)

def db_com():
    return conn.commit()

def url_pas(data):
    return parse.quote(data).replace('/','%2F')
    
def db_get():
    return curs.fetchall()

def sha224(data):
    return hashlib.sha224(bytes(data, 'utf-8')).hexdigest()
    
db_ex = curs.execute
db_pas = pymysql.escape_string

db_ex("use " + set_data['db'])

def diff(seqm):
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if(opcode == 'equal'):
            output.append(seqm.a[a0:a1])
        elif(opcode == 'insert'):
            output.append("<span style='background:#CFC;'>" + seqm.b[b0:b1] + "</span>")
        elif(opcode == 'delete'):
            output.append("<span style='background:#FDD;'>" + seqm.a[a0:a1] + "</span>")
        elif(opcode == 'replace'):
            output.append("<span style='background:#CFC;'>" + seqm.b[b0:b1] + "</span><span style='background:#FDD;'>" + seqm.a[a0:a1] + "</span>")
        else:
            output.append(seqm.a[a0:a1])
            
    return ''.join(output)
           
def admin_check(num, session):
    ip = ip_check(session) 
    db_ex("select acl from user where id = '" + db_pas(ip) + "'")
    user = db_get()
    if(user):
        db_ex("select acl from alist where name = '" + db_pas(user[0]['acl']) + "'")
        adata = db_get()
        if(adata):
            i = 0
            while(True):
                try:
                    if(num == 1 and adata[i]['acl'] == 'ban'):
                        return 1
                        
                        break
                    elif(num == 2 and adata[i]['acl'] == 'mdel'):
                        return 1
                        
                        break
                    elif(num == 3 and adata[i]['acl'] == 'toron'):
                        return 1
                        
                        break
                    elif(num == 4 and adata[i]['acl'] == 'check'):
                        return 1
                        
                        break
                    elif(num == 5 and adata[i]['acl'] == 'acl'):
                        return 1
                        
                        break
                    elif(num == 6 and adata[i]['acl'] == 'hidel'):
                        return 1
                        
                        break
                    elif(adata[i]['acl'] == 'owner'):
                        return 1
                        
                        break
                    else:
                        i += 1
                except:
                    break
                
def include_check(name, data):
    if(re.search('^틀:', name)):
        db_ex("select * from back where title = '" + db_pas(name) + "' and type = 'include'")
        back = db_get()
        if(back):
            i = 0

            while(True):
                try:
                    namumark(back[i]['link'], data)
                except:
                    break
                    
                i += 1
    
def login_check(session):
    if(session.get('Now') == True):
        return 1
    else:
        return 0

def ip_pas(raw_ip, num):
    yes = re.search("([^-]*)\s\-\s(Close|Reopen|Stop|Restart|Admin|Agreement|Settlement)$", raw_ip)
    if(yes):
        results = yes.groups()
        
        db_ex("select title from data where title = '사용자:" + db_pas(results[0]) + "'")
        row = db_get()
        if(row):
            ip = '<a href="/w/' + url_pas('사용자:' + results[0]) + '">' + results[0] + '</a> - ' + results[1]
        else:
            ip = '<a class="not_thing" href="/w/' + url_pas('사용자:' + results[0]) + '">' + results[0] + '</a> - ' + results[1]
    elif(re.search("\.", raw_ip)):
        ip = raw_ip
    else:
        db_ex("select title from data where title = '사용자:" + db_pas(raw_ip) + "'")
        row = db_get()
        if(row):
            ip = '<a href="/w/' + url_pas('사용자:' + raw_ip) + '">' + raw_ip + '</a>'
        else:
            ip = '<a class="not_thing" href="/w/' + url_pas('사용자:' + raw_ip) + '">' + raw_ip + '</a>'
            
    if(num == 1):
        if(yes):
            ip += ' <a href="/user/' + url_pas(results[0]) + '/topic/1">(기록)</a>'
        else:
            ip += ' <a href="/user/' + url_pas(raw_ip) + '/topic/1">(기록)</a>'
    elif(num == 2):
        if(yes):
            ip += ' <a href="/record/' + url_pas(results[0]) + '/n/1">(기록)</a> <a href="/user/' + url_pas(results[0]) + '/topic/1">(토론 기록)</a>'
        else:
            ip += ' <a href="/record/' + url_pas(raw_ip) + '/n/1">(기록)</a> <a href="/user/' + url_pas(raw_ip) + '/topic/1">(토론 기록)</a>'        
    else:
        if(yes):
            ip += ' <a href="/record/' + url_pas(results[0]) + '/n/1">(기록)</a>'
        else:
            ip += ' <a href="/record/' + url_pas(raw_ip) + '/n/1">(기록)</a>'

    return ip

def ip_check(session):
    if(session.get('Now') == True):
        ip = format(session['DREAMER'])
    else:
        if(request.environ.get('HTTP_X_FORWARDED_FOR')):
            ip = request.environ.get('HTTP_X_FORWARDED_FOR')
        else:
            ip = request.environ.get('REMOTE_ADDR')

    return ip

def custom_css_user(session):
    if(session.get('Now') == True):
        try:
            data = format(session['Daydream'])
        except:
            data = ''
    else:
        data = ''

    return data

def acl_check(session, ip, name):
    m = re.search("^사용자:(.*)", name)
    n = re.search("^파일:(.*)", name)
    if(m):
        g = m.groups()
        if(ip == g[0]):
            if(re.search("\.", g[0])):
                return 1
            else:
                db_ex("select * from ban where block = '" + db_pas(ip) + "'")
                rows = db_get()
                if(rows):
                    return 1
                else:
                    return 0
        else:
            return 1
    elif(n):
        if(not owner_check(session)  == 1):
            return 1
    else:
        b = re.search("^([0-9](?:[0-9]?[0-9]?)\.[0-9](?:[0-9]?[0-9]?))", ip)
        if(b):
            results = b.groups()
            db_ex("select * from ban where block = '" + db_pas(results[0]) + "' and band = 'O'")
            rowss = db_get()
            if(rowss):
                return 1
            else:
                db_ex("select * from ban where block = '" + db_pas(ip) + "'")
                rows = db_get()
                if(rows):
                    return 1
                else:
                    db_ex("select acl from data where title = '" + db_pas(name) + "'")
                    row = db_get()
                    if(row):
                        db_ex("select * from user where id = '" + db_pas(ip) + "'")
                        rows = db_get()
                        if(row[0]['acl'] == 'user'):
                            if(rows):
                                return 0
                            else:
                                return 1
                        elif(row[0]['acl'] == 'admin'):
                            if(rows):
                                if(rows[0]['acl'] == 'admin' or rows[0]['acl'] == 'owner'):
                                    return 0
                                else:
                                    return 1
                            else:
                                return 1
                        else:
                            return 0
                    else:
                        return 0
        else:
            db_ex("select * from ban where block = '" + db_pas(ip) + "'")
            rows = db_get()
            if(rows):
                return 1
            else:
                db_ex("select acl from data where title = '" + db_pas(name) + "'")
                row = db_get()
                if(row):
                    db_ex("select * from user where id = '" + db_pas(ip) + "'")
                    rows = db_get()
                    if(row[0]['acl'] == 'user'):
                        if(rows):
                            return 0
                        else:
                            return 1
                    elif(row[0]['acl'] == 'admin'):
                        if(rows):
                            if(rows[0]['acl'] == 'admin' or rows[0]['acl'] == 'owner'):
                                return 0
                            else:
                                return 1
                        else:
                            return 1
                    else:
                        return 0
                else:
                    return 0

def ban_check(ip):
    b = re.search("^([0-9](?:[0-9]?[0-9]?)\.[0-9](?:[0-9]?[0-9]?))", ip)
    if(b):
        results = b.groups()
        db_ex("select * from ban where block = '" + db_pas(results[0]) + "' and band = 'O'")
        rowss = db_get()
        if(rowss):
            return 1
        else:
            db_ex("select * from ban where block = '" + db_pas(ip) + "'")
            rows = db_get()
            if(rows):
                return 1
            else:
                return 0
    else:
        db_ex("select * from ban where block = '" + db_pas(ip) + "'")
        rows = db_get()
        if(rows):
            return 1
        else:
            return 0
        
def topic_check(ip, name, sub):
    b = re.search("^([0-9](?:[0-9]?[0-9]?)\.[0-9](?:[0-9]?[0-9]?))", ip)
    if(b):
        results = b.groups()
        db_ex("select * from ban where block = '" + db_pas(results[0]) + "' and band = 'O'")
        rowss = db_get()
        if(rowss):
            return 1
        else:
            db_ex("select * from ban where block = '" + db_pas(ip) + "'")
            rows = db_get()
            if(rows):
                return 1
            else:
                db_ex("select * from stop where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "'")
                rows = db_get()
                if(rows):
                    return 1
                else:
                    return 0
    else:
        db_ex("select * from ban where block = '" + db_pas(ip) + "'")
        rows = db_get()
        if(rows):
            return 1
        else:
            db_ex("select * from stop where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "'")
            rows = db_get()
            if(rows):
                return 1
            else:
                return 0

def get_time():
    now = time.localtime()
    date = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    
    return date

def rd_plus(title, sub, date):
    db_ex("select * from rd where title = '" + db_pas(title) + "' and sub = '" + db_pas(sub) + "'")
    rd = db_get()
    if(rd):
        db_ex("update rd set date = '" + db_pas(date) + "' where title = '" + db_pas(title) + "' and sub = '" + db_pas(sub) + "'")
    else:
        db_ex("insert into rd (title, sub, date) value ('" + db_pas(title) + "', '" + db_pas(sub) + "', '" + db_pas(date) + "')")
    db_com()
    
def rb_plus(block, end, today, blocker, why):
    db_ex("insert into rb (block, end, today, blocker, why) value ('" + db_pas(block) + "', '" + db_pas(end) + "', '" + today + "', '" + db_pas(blocker) + "', '" + db_pas(why) + "')")
    db_com()

def history_plus(title, data, date, ip, send, leng):
    db_ex("select * from history where title = '" + db_pas(title) + "' order by id+0 desc limit 1")
    rows = db_get()
    if(rows):
        number = int(rows[0]['id']) + 1
        db_ex("insert into history (id, title, data, date, ip, send, leng) value ('" + str(number) + "', '" + db_pas(title) + "', '" + db_pas(data) + "', '" + date + "', '" + db_pas(ip) + "', '" + db_pas(send) + "', '" + leng + "')")
        db_com()
    else:
        db_ex("insert into history (id, title, data, date, ip, send, leng) value ('1', '" + db_pas(title) + "', '" + db_pas(data) + "', '" + date + "', '" + db_pas(ip) + "', '" + db_pas(send + ' (새 문서)') + "', '" + leng + "')")
        db_com()

def leng_check(a, b):
    if(a < b):
        c = b - a
        c = '+' + str(c)
    elif(b < a):
        c = a - b
        c = '-' + str(c)
    else:
        c = '0'
        
    return c