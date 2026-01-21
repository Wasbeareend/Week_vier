import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

app = Flask(__name__)
app.jinja_env.filters["usd"] = usd

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]

    positions = db.execute("""
        SELECT symbol, SUM(shares) AS shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
        HAVING SUM(shares) > 0
        ORDER BY symbol
    """, user_id)

    holdings = []
    stocks_total = 0

    for p in positions:
        stock = lookup(p["symbol"])
        if stock is None:
            continue

        price = stock["price"]
        total = p["shares"] * price
        stocks_total += total

        holdings.append({
            "symbol": p["symbol"],
            "name": stock["name"],
            "shares": p["shares"],
            "price": price,
            "total": total
        })

    cash_row = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = cash_row[0]["cash"]

    grand_total = stocks_total + cash

    return render_template(
        "index.html",
        holdings=holdings,
        cash=cash,
        grand_total=grand_total
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")

    symbol = request.form.get("symbol", "").strip().upper()
    shares_str = request.form.get("shares", "").strip()

    if not symbol:
        return apology("must provide symbol", 400)

    stock = lookup(symbol)
    if stock is None:
        return apology("invalid symbol", 400)

    try:
        shares = int(shares_str)
        if shares <= 0:
            raise ValueError
    except ValueError:
        return apology("shares must be a positive integer", 400)

    user_id = session["user_id"]
    cash_row = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = cash_row[0]["cash"]

    cost = shares * stock["price"]
    if cost > cash:
        return apology("can't afford", 400)

    db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", cost, user_id)

    db.execute(
        "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
        user_id, symbol, shares, stock["price"]
    )

    return redirect("/")


@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]

    txs = db.execute("""
        SELECT symbol, shares, price, transacted_at
        FROM transactions
        WHERE user_id = ?
        ORDER BY transacted_at DESC, id DESC
    """, user_id)

    for t in txs:
        t["type"] = "BUY" if t["shares"] > 0 else "SELL"
        t["abs_shares"] = abs(t["shares"])

    return render_template("history.html", transactions=txs)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username:
        return apology("must provide username", 403)
    if not password:
        return apology("must provide password", 403)

    rows = db.execute("SELECT * FROM users WHERE username = ?", username)

    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        return apology("invalid username and/or password", 403)

    session["user_id"] = rows[0]["id"]
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")

    symbol = request.form.get("symbol", "").strip().upper()
    if not symbol:
        return apology("must provide symbol", 400)

    stock = lookup(symbol)
    if stock is None:
        return apology("invalid symbol", 400)

    return render_template("quoted.html", stock=stock)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirmation = request.form.get("confirmation", "")

    if not username:
        return apology("must provide username", 400)
    if not password:
        return apology("must provide password", 400)
    if not confirmation:
        return apology("must confirm password", 400)
    if password != confirmation:
        return apology("passwords must match", 400)

    pw_hash = generate_password_hash(password)

    try:
        new_id = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username, pw_hash
        )
    except ValueError:
        return apology("username already exists", 400)

    session["user_id"] = new_id
    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    user_id = session["user_id"]

    if request.method == "GET":
        symbols_rows = db.execute("""
            SELECT symbol
            FROM transactions
            WHERE user_id = ?
            GROUP BY symbol
            HAVING SUM(shares) > 0
            ORDER BY symbol
        """, user_id)

        symbols = [r["symbol"] for r in symbols_rows]
        return render_template("sell.html", symbols=symbols)

    symbol = request.form.get("symbol", "").strip().upper()
    shares_str = request.form.get("shares", "").strip()

    if not symbol:
        return apology("must select symbol", 400)

    try:
        shares = int(shares_str)
        if shares <= 0:
            raise ValueError
    except ValueError:
        return apology("shares must be a positive integer", 400)

    owned_row = db.execute("""
        SELECT COALESCE(SUM(shares), 0) AS owned
        FROM transactions
        WHERE user_id = ? AND symbol = ?
    """, user_id, symbol)

    owned = owned_row[0]["owned"]
    if shares > owned:
        return apology("too many shares", 400)

    stock = lookup(symbol)
    if stock is None:
        return apology("invalid symbol", 400)

    proceeds = shares * stock["price"]

    db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", proceeds, user_id)

    db.execute(
        "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
        user_id, symbol, -shares, stock["price"]
    )

    return redirect("/")