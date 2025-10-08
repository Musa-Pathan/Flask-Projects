from flask import Flask, render_template, request, redirect, session
import mysql.connector

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="Expense"
)


def homepage():
    if "uid" not in session:
        return redirect("/login")
    
    val = (session["uid"],)
    cursor = con.cursor(dictionary=True)

    # Total income
    cursor.execute("SELECT SUM(income) AS total_income FROM user_expense WHERE user_id=%s", val)
    result = cursor.fetchone()
    total_income = result['total_income'] if result and result['total_income'] else 0

    # Latest balance
    cursor.execute("""
        SELECT balance 
        FROM user_expense 
        WHERE user_id=%s AND balance IS NOT NULL 
        ORDER BY expense_date DESC, expense_id DESC 
        LIMIT 1
    """, val)
    result = cursor.fetchone()
    total_amt = result['balance'] if result and result['balance'] is not None else 0

    # Total expense
    cursor.execute("SELECT SUM(expense_amt) AS total_exp FROM user_expense WHERE user_id=%s", val)
    result = cursor.fetchone()
    total_exp = result['total_exp'] if result and result['total_exp'] else 0

    # Recent transactions (last 5)
    cursor.execute("""
        SELECT expense_date, expense_type, expense_amt, income, balance, transaction_type
        FROM user_expense
        WHERE user_id=%s
        ORDER BY expense_date DESC, expense_id DESC
        LIMIT 5
    """, val)
    transactions = cursor.fetchall()
    cursor.close()

    return render_template(
        "homepage.html",
        total_amt=total_amt,
        total_income=total_income,
        total_exp=total_exp,
        transactions=transactions
    )


def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        uname = request.form.get("username")
        password = request.form.get("password")

        cursor = con.cursor()
        sql = "SELECT COUNT(*) FROM userData WHERE uname=%s AND password=%s"
        val = (uname, password)
        cursor.execute(sql, val)
        count = cursor.fetchone()
        cursor.close()

        if count[0] == 1:
            # User is valid
            cursor = con.cursor()
            sql = "SELECT * FROM userData WHERE uname=%s"
            val = (uname,)
            cursor.execute(sql, val)
            uid = cursor.fetchone()
            cursor.close()

            session['uid'] = uid[0]
            session["username"] = uname
            return redirect("/homepage")
        else:
            return redirect("/login")


def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        uname = request.form.get("username")
        password = request.form.get("password")

        cursor = con.cursor()
        sql = "SELECT COUNT(*) FROM userData WHERE uname=%s"
        val = (uname,)
        cursor.execute(sql, val)
        count = cursor.fetchone()

        if count[0] == 1:
            # User already exists
            cursor.close()
            return redirect("/register")
        else:
            # Create new user
            sql = "INSERT INTO userData (uname, password) VALUES (%s, %s)"
            val = (uname, password)
            cursor.execute(sql, val)
            con.commit()
            cursor.close()
            return redirect("/login")


def addExpense():
    if request.method == "GET":
        return render_template("addExpense.html")
    else:
        expense_date = request.form.get("expense_date")
        expense_type = request.form.get("expense_type")
        note = request.form.get("note")
        expense_amt = float(request.form.get("expense_amt") or 0)
        balance = float(request.form.get("balance") or 0)
        income = float(request.form.get("income") or 0)
        transaction_type = request.form.get("transaction_type")

        if transaction_type.lower() == "income":
            new_balance = balance + income
        else:
            new_balance = balance - expense_amt

        cursor = con.cursor()
        sql = """
        INSERT INTO user_expense 
        (user_id, expense_date, expense_type, note, expense_amt, balance, income, transaction_type)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """
        val = (session['uid'], expense_date, expense_type, note, expense_amt, new_balance, income, transaction_type)
        cursor.execute(sql, val)
        con.commit()
        cursor.close()

        return redirect("/homepage")

def editExpense(expense_id):
    if "uid" not in session:
        return redirect("/login")

    cursor = con.cursor()
    sql = "SELECT * FROM user_expense WHERE expense_id=%s AND user_id=%s"
    val = (expense_id,session["uid"],)
    cursor.execute(sql,val)
    expense = cursor.fetchone()
    
    if request.method == "GET":
        return render_template("editExpense.html", expense=expense)

    else:
        expense_date = request.form.get("expense_date")
        expense_type = request.form.get("expense_type")
        note = request.form.get("note")
        expense_amt = float(request.form.get("expense_amt") or 0)
        income = float(request.form.get("income") or 0)
        transaction_type = request.form.get("transaction_type")

        cursor = con.cursor()
        sql = """
        UPDATE user_expense 
        SET expense_date=%s, expense_type=%s, note=%s, expense_amt=%s, income=%s, transaction_type=%s
        WHERE expense_id=%s AND user_id=%s
        """
        val = (expense_date, expense_type, note, expense_amt, income, transaction_type, expense_id, session["uid"])
        cursor.execute(sql, val)
        con.commit()
        cursor.close()

        return redirect("/showAllExp")
    
def deleteExpense(expense_id):
    if "uid" not in session:
        return redirect("/login")

    cursor = con.cursor()
    sql = "DELETE FROM user_expense WHERE expense_id=%s AND user_id=%s"
    cursor.execute(sql, (expense_id, session["uid"]))
    con.commit()
    cursor.close()

    return redirect("/showAllExp")


def showAllExp():
    if "uid" not in session:
        return redirect("/login")

    cursor = con.cursor()
    sql = "SELECT * FROM user_expense WHERE user_id=%s"
    val = (session['uid'],)
    cursor.execute(sql, val)
    expenses = cursor.fetchall()
    cursor.close()

    return render_template("showAllExp.html", expenses=expenses)


def logout():
    session.clear()
    return redirect("/login")