from flask import Flask, request, render_template
import mysql.connector
import re


config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'Maxim'
    }


db = mysql.connector.connect(**config)

app = Flask(__name__)


def filtr(g):
    pattern = r'[^\w+]'
    g = re.sub(pattern, ' ' , g)
    g = re.sub('_', ' ' , g)
    if g[0] == ' ':
        g = g[1:]
    print(g)
    return g


def find(p, n):
    cursor = db.cursor()
    cursor.execute("SELECT @myLeft := lft, @myRight := rgt FROM nested_category WHERE id = '{0}';".format(p))
    cursor.execute("SELECT name FROM nested_category WHERE BETWEEN @myLeft AND @myRight;")
    nam = cursor.fetchone()
    print(nam)
    for x in nam:
        if x == n:
            return False
    return True


@app.route('/getL')
def getL():
    cursor = db.cursor()
    sql = "SELECT * FROM nested_category"
    cursor.execute(sql)
    results = cursor.fetchall()
    return str(results)


@app.route("/add")
def add():
    n = str(request.args.get('name'))
    p = str(request.args.get('parent'))
    cursor = db.cursor()
    if n == '' or p =='':
        return("Введено пустое значение!")
    p = filtr(p)
    n = filtr(n)
    if find(p,n):
        cursor.execute("LOCK TABLE nested_category WRITE;")
        cursor.execute("SELECT @myLeft := lft FROM nested_category WHERE id = '{0}';".format(p))
        cursor.execute("UPDATE nested_category SET rgt = rgt + 2 WHERE rgt > @myLeft;")
        cursor.execute("UPDATE nested_category SET lft = lft + 2 WHERE lft > @myLeft;")
        cursor.execute("INSERT INTO nested_category(name, lft, rgt) VALUES('{0}', @myLeft + 1, @myLeft + 2);".format(n))
        cursor.execute("UNLOCK TABLES;")
        da = cursor.fetchone()
        return "Logged in successfully"
    else:
        return "Данное значение уже есть"


@app.route("/dell")
def dell():
    d = str(request.args.get('d'))
    cursor = db.cursor()
    #return(sqll,val)
    cursor.execute("SET SQL_SAFE_UPDATES = 0;")
    cursor.execute("LOCK TABLE nested_category WRITE;")
    cursor.execute("""  SELECT @myLeft := lft, @myRight := rgt, @myWidth := rgt - lft + 1
                        FROM nested_category
                        WHERE id = %s;   """,d)
    data = cursor.fetchone()
    cursor.execute("DELETE FROM nested_category WHERE lft BETWEEN @myLeft AND @myRight;")
    cursor.execute("UPDATE nested_category SET rgt = rgt - @myWidth WHERE rgt > @myRight;")
    cursor.execute("UPDATE nested_category SET lft = lft - @myWidth WHERE lft > @myRight;")
    cursor.execute("UNLOCK TABLES;")
    data = cursor.fetchone()
    return str(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0')


