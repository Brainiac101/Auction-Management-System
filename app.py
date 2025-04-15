from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_apscheduler import APScheduler
from werkzeug.serving import is_running_from_reloader
from datetime import datetime
import mysql.connector
import os
import sys
from mysql.connector import Error

app = Flask(__name__)
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)

@scheduler.task('interval', id='check_auctions', seconds=30, max_instances=1)
def check_ended_auctions():
    with app.app_context():
        global db
        if(db != None):
            cursor = db.cursor(dictionary=True, buffered=True)
            start_time = datetime.now()
                # Find auctions that just ended
            cursor.execute("""
                    SELECT A.AuctionID, A.ItemID, MAX(B.BidAmount) AS HighestBid
                    FROM Auction A JOIN Bid B
                    ON A.AuctionID = B.AuctionID AND A.ItemID = B.ItemID
                    WHERE A.EndTime <= %s
                    GROUP BY A.AuctionID, A.ItemID
                """, (start_time,))
            ended_auctions = cursor.fetchall()
            print("*" * 20)
            print("\n",ended_auctions,"\n")
            print("*" * 20)

            for auction in ended_auctions:
                auction_id = auction['AuctionID']
                item_id = auction['ItemID']
                highest_bid = auction['HighestBid']
                cursor.execute("Select WinnerID from Item where ItemID = %s", (item_id,))
                curr = cursor.fetchone()
                if curr['WinnerID'] is None:
                    cursor.execute("""
                            SELECT BidderID, BidAmount FROM Bid
                            WHERE AuctionID = %s AND ItemID = %s
                            ORDER BY BidAmount DESC LIMIT 1
                    """, (auction_id, item_id))
                    winner = cursor.fetchone()
                    if winner:
                        cursor.execute("""UPDATE Item SET WinnerID = %s WHERE ItemID = %s""", (winner['BidderID'], item_id))
                        db.commit()

                        cursor.execute("""UPDATE Seller Set TotalSales = %s Where ItemID = %s""", (winner['BidAmount'], item_id))
                        db.commit()

                        cursor.execute("Select * from User WHERE UserID = %s", ( winner['BidderID'], ))
                        user = cursor.fetchone()
                            
                        print(user["Balance"], winner['BidAmount'])
                        bal = max(user["Balance"] - winner['BidAmount'], 0)
                        cursor.execute("UPDATE User SET Balance = %s WHERE UserID = %s", (bal, user['UserID']))
                        db.commit()
                        # session['balance'] = bal

                        cursor.execute("UPDATE User SET Balance = Balance + %s WHERE UserID = (SELECT UserID FROM Seller WHERE ItemID = %s)", (winner['BidAmount'], item_id))
                        db.commit()
                            
                cursor.close()

d = {1: '''SELECT I.ItemID, I.Name, I.Description, C.Title AS CategoryTitle FROM Item I JOIN Category C ON I.CategoryID = C.CategoryID;''',
     2: '''SELECT A.AuctionID, I.Name AS ItemName, MAX(B.BidAmount) AS HighestBid FROM Bid B JOIN Auction A ON B.AuctionID = A.AuctionID JOIN Item I ON A.ItemID = I.ItemID GROUP BY A.AuctionID, I.Name;''',
     3: '''SELECT S.UserID, U.Username, SUM(S.TotalSales) AS TotalSales FROM Seller S JOIN User U ON S.UserID = U.UserID GROUP BY S.UserID, U.Username ORDER BY TotalSales DESC;''', 
     4: '''SELECT A.AuctionID, I.Name AS ItemName, A.EndTime FROM Auction A JOIN Item I ON A.ItemID = I.ItemID WHERE A.EndTime < NOW() AND I.WinnerID IS NULL;''', 
     5: '''SELECT A.AuctionID, I.Name AS ItemName, U.Username AS Seller, MAX(B.BidAmount) AS HighestBid FROM Auction A JOIN Item I ON A.ItemID = I.ItemID JOIN Seller S ON I.ItemID = S.ItemID JOIN User U ON S.UserID = U.UserID LEFT JOIN Bid B ON A.AuctionID = B.AuctionID GROUP BY A.AuctionID, I.Name, U.Username;''', 
     6: '''SELECT C.Title AS CategoryTitle, COUNT(I.ItemID) AS ItemCount FROM Category C LEFT JOIN Item I ON C.CategoryID = I.CategoryID GROUP BY C.Title;''', 
     7: '''SELECT ItemID, Name FROM Item WHERE ItemID IN (SELECT ItemID FROM Auction GROUP BY ItemID HAVING COUNT(AuctionID) > 1);''', 
     8: '''SELECT AuctionID, ItemID, StartTime, EndTime FROM Auction WHERE StartTime = (SELECT MAX(StartTime) FROM Auction AS A WHERE A.ItemID = Auction.ItemID);''', 
     9: '''SELECT UserID, Username FROM User WHERE UserID IN (SELECT BidderID FROM Bid GROUP BY BidderID HAVING COUNT(*) = (SELECT MAX(BidCount) FROM (SELECT COUNT(*) AS BidCount FROM Bid GROUP BY BidderID) AS BidStats));''',
     10: '''SELECT DISTINCT U.UserID, U.Username
FROM User U
JOIN Seller S ON U.UserID = S.UserID
JOIN Bidder B ON U.UserID = B.UserID;
''',
11:'''SELECT B.BidderID, U.Username, SUM(B.BidAmount) AS TotalBidAmount
FROM Bid B
JOIN User U ON B.BidderID = U.UserID
GROUP BY B.BidderID, U.Username
ORDER BY TotalBidAmount DESC
LIMIT 3;''',
     12: '''SELECT AuctionID, ItemID, Duration 
FROM Auction 
WHERE Duration > (
    SELECT AVG(Duration) FROM Auction
);''', 
     13: '''SELECT u.UserID, u.Username, b.AuctionID, COUNT(b.BidAmount) AS TotalBids
FROM User u
JOIN Bid b ON u.UserID = b.BidderID
GROUP BY b.AuctionID, u.UserID, u.Username
HAVING COUNT(b.BidAmount) = (
    SELECT MAX(BidCount)
    FROM (
        SELECT AuctionID, BidderID, COUNT(BidAmount) AS BidCount
        FROM Bid
        GROUP BY AuctionID, BidderID
    ) AS BidStats
    WHERE BidStats.AuctionID = b.AuctionID
);''', 
     14: '''SELECT B.BidderID, U.Username, U.Balance, B.BidAmount, B.AuctionID, I.Name AS ItemName
FROM Bid B
JOIN User U ON B.BidderID = U.UserID
JOIN Item I ON B.ItemID = I.ItemID
WHERE B.AuctionID = %s;''', 
     15: '''SELECT
    b.UserID, 
    u.Username, 
    b.BidLimit, 
    bd.BidAmount
FROM Bidder b
JOIN User u ON b.UserID = u.UserID
JOIN Bid bd ON b.UserID = bd.BidderID 
    AND b.AuctionID = bd.AuctionID 
    AND b.ItemID = bd.ItemID
WHERE bd.BidAmount > b.BidLimit;''',
     16: '''
SELECT U.Username, COUNT(*) AS NumAuctions
FROM User U
JOIN Bidder B ON U.UserID = B.UserID
JOIN Auction A ON B.AuctionID = A.AuctionID
GROUP BY U.UserID, U.Username
UNION ALL
SELECT U.Username, COUNT(*) AS NumAuctions
FROM User U
JOIN Seller S ON U.UserID = S.UserID
JOIN Item I ON S.ItemID = I.ItemID
JOIN Auction A ON I.ItemID = A.ItemID
GROUP BY U.UserID, U.Username;
'''}
d1 = {1: '''Retrieve all items with their respective category titles.''',
     2: '''Get the highest bid for each auction.''',
     3: '''Retrieve the total sales amount for each seller.''', 
     4: '''Get all auctions that have ended but have no winner assigned.''', 
     5: '''Retrieve details of any auction including seller, item, and highest bid.''', 
     6: '''Count the number of items in each category''', 
     7: '''Find items that were auctioned more than once.''', 
     8: '''Find the Latest auction for each time.''', 
     9: '''Find Users Who Have Placed the Most Bids in any Auction.''',
     10: '''Find users who have participated as both sellers and bidders''',
     11:'''Get the top 3 bidders who have placed the highest total bid amount''',
     12: '''Find Auctions That Lasted Longer Than the Average Duration''', 
     13: '''Find Users Who Have Placed the Most Bids in every Auction''', 
     14: '''Retrieve all bids for a specific auction along with bidder details''', 
     15: '''Get all bidders who have exceeded their bid limit''',
     16: '''Get a list of users and the number of auctions they have participated in (either as a bidder or as a seller)'''}
#5,9,13
def initialize_database():
    # Temporary connection to check/create database
    temp_db = mysql.connector.connect(
        host="localhost",
        user=arg1,
        password=arg2
    )
    temp_cursor = temp_db.cursor()
    temp_cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in temp_cursor.fetchall()]
    
    if "auction" not in databases:
        temp_cursor.execute("CREATE DATABASE auction")
        temp_db.commit()
        
        temp_cursor.execute("USE auction")
        sql_file_path = os.path.join(os.getcwd(), "sql/auction.sql")
        sql_file_path2 = os.path.join(os.getcwd(), "sql/auction-records-insert.sql")
        
        with open(sql_file_path, 'r') as f:
            sql_commands = f.read().split(";")
        with open(sql_file_path2, 'r') as f2:
            sql_commands2 = f2.read().split(";")

        for command in sql_commands:
            if command.strip():
                try:
                    temp_cursor.execute(command)
                except mysql.connector.Error as err:
                    continue
        for command in sql_commands2:
            if command.strip():
                try:
                    temp_cursor.execute(command)
                except mysql.connector.Error as err:
                    continue
        temp_db.commit()
        print("Database initialized successfully.")

    temp_cursor.close()
    temp_db.close()

    # Return a new connection to the 'auction' database
    return mysql.connector.connect(
        host="localhost",
        user=arg1,
        password=arg2,
        database="auction"
    )


app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    global db
    cursor = db.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("""
            SELECT i.ItemID, i.Name, i.BasePrice, c.Title as Category, 
            a.StartTime, a.EndTime, MAX(B.BidAmount) AS HighestBid
            FROM Item i 
            JOIN Auction a ON i.ItemID = a.ItemID 
            LEFT Join Bid B on a.AuctionID = B.AuctionID AND i.ItemID = B.ItemID
            LEFT JOIN Category c ON i.CategoryID = c.CategoryID WHERE a.EndTime > NOW()
            GROUP BY i.ItemID, a.AuctionID
            LIMIT 5
        """)
        items = cursor.fetchall()
        for i in items:
            if i['HighestBid'] == None:
                i['HighestBid']= "No bids placed yet"
    finally:
        cursor.close()
    return render_template('home.html', items=items, current_page=request.endpoint)

@app.route('/register', methods=['GET', 'POST'])
def register():
    global db
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        balance = request.form['balance']
        if ValueError:
            flash("Invalid balance amount", "danger")
            return redirect(url_for('register'))

        cursor = db.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute("""
                INSERT INTO User (Username, Password, Balance) 
                VALUES (%s, %s, %s)
            """, (username, password, balance))
            db.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('auctions'))
        except Error as e:
            db.rollback()
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global db
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username=="admin" and password=="admin":
            session['user_id']="admin"
            session['password']="admin"
            return redirect(url_for('admin'))
        cursor = db.cursor(dictionary=True, buffered=True)
        try:
            
            cursor.execute("""SELECT * FROM User WHERE Username = (%s) AND Password = (%s)""", (username, password))
            items = cursor.fetchone()
            if(len(items) == 0):
                flash("Invalid username or password", "danger")
                return redirect(url_for('login'))
            else:
                if items['Username']=="admin" and items["Password"]=="admin":
                    session['user_id']=items['Username']
                    session['password']=items['Password']
                    return redirect(url_for('admin'))
                session['user_id']=items['Username']
                session['password']=items['Password']
                session['balance']=float(items['Balance'])
                session['primary']=items['UserID']
                
            # flash("Registration successful!", "success")
            return redirect(url_for('home'))
        
        except Error as e:
            db.rollback()
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# @app.before_request
# def update_session_balance():
#     global db   
#     user_id = session.get("user_id")
#     if user_id:
#         cursor = db.cursor(dictionary=True)
#         cursor.execute("SELECT Balance FROM User WHERE Username = %s", (user_id,))
#         user = cursor.fetchone()
#         print("****")
#         print(user)
#         print("****")
#         if user:
#             session["balance"] = user["Balance"]
#             print("****")
#             print(session["balance"])
#             print("****")

@app.route('/search')
def search():
    global db
    query = request.args.get('q',)
    cursor = db.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("""
            SELECT i.ItemID, i.Name, i.BasePrice, c.Title as Category, 
            a.StartTime, a.EndTime, MAX(B.BidAmount) AS HighestBid
            FROM Item i 
            JOIN Auction a ON i.ItemID = a.ItemID 
            LEFT Join Bid B on a.AuctionID = B.AuctionID AND i.ItemID = B.ItemID
            LEFT JOIN Category c ON i.CategoryID = c.CategoryID WHERE a.EndTime > NOW()
            AND i.Name LIKE %s OR c.Title LIKE %s
            GROUP BY i.ItemID, a.AuctionID
            LIMIT 5
        """, ('%'+query+'%','%'+query+'%'))
        items = cursor.fetchall()
        print(items)
    finally:    
        cursor.close()
    return render_template('search_results.html', items=items, query=query)

@app.route('/admin')
def admin():
    global db
    try:
        cursor=db.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM User")
        result=cursor.fetchall()
        cursor.execute("SELECT Auction.AuctionID as AuctionID, Auction.ItemID as ItemID, Item.Name as ItemName, Category.Title as Category, Item.BasePrice as BasePrice, Auction.StartTime as StartTime, Auction.EndTime as EndTime, MAX(BidAmount) as HighestBid FROM Auction join Item on Auction.ItemID=Item.ItemID join Bid on Auction.ItemID = Bid.ItemID AND Auction.AuctionID = Bid.AuctionID join Category on Category.CategoryID=Item.CategoryID GROUP BY Auction.AuctionID, Auction.ItemID")
        result2=cursor.fetchall()
    finally:
        cursor.close()
    return render_template('admin.html',users=result,auctions=result2)

@app.route('/seller_profile')
def seller_profile():
    global db
    if session['user_id'] == None:
        return redirect(url_for('login'))
    else:
        cursor=db.cursor(dictionary=True, buffered=True)
        cursor1=db.cursor(dictionary=True, buffered=True)
        cursor2=db.cursor(dictionary=True, buffered=True)
        cursor3=db.cursor(dictionary=True, buffered=True)
        try:
            cursor3.execute("SELECT * FROM Seller where UserID=%s",(session['primary'],))
            user=cursor3.fetchone()

            cursor1.execute("SELECT * from Item i join Seller s on i.ItemID=s.ItemID where s.UserID=%s and i.WinnerID is NULL and i.ItemID not in (SELECT a.itemID from Auction A);",(session['primary'],))
            items1=cursor1.fetchall()
            print(items1)

            cursor2.execute("SELECT * FROM Item I JOIN Seller S ON I.ItemID = S.ItemID WHERE S.UserID = %s AND I.WinnerID IS NOT NULL", (session['primary'],))
            items2 = cursor2.fetchall()
            print(items2)
            
            cursor.execute("SELECT * FROM Item I JOIN Seller S ON I.ItemID = S.ItemID JOIN Auction A ON I.ItemID = A.ItemID WHERE S.UserID = %s AND A.EndTime > NOW()", (session['primary'],))
            items = cursor.fetchall()

            cursor1.execute("SELECT SUM(TotalSales) AS sales FROM Seller WHERE UserID=%s GROUP BY UserID;",(session['primary'],))
            sales=cursor1.fetchone()
            sales = sales['sales'] if sales else None

            cursor2.execute("SELECT DISTINCT C.Title FROM Category AS C;")
            categories = cursor2.fetchall()

        finally:
            cursor1.close()
            cursor2.close()
            cursor3.close()
            cursor.close()
    return render_template('seller_profile.html', user=user, items = items, items1 = items1, items2 = items2, sales=sales, categories=categories)

@app.route('/bidder_profile')
def bidder_profile():
    global db
    cursor = db.cursor(dictionary=True, buffered=True)
    try:
        # cursor.execute("SELECT B.Item_ID, MAX(BidAmount)  from Bid B join Auction A on A.AuctionID=B.AuctionID and A.ItemID=B.ItemID where B.User_ID=%s and A.EndTime>NOW() GROUP BY A.AuctionID, I.ItemID, B.BidderID", (session['primary'],))
        add_amount = request.args.get('add_amount')
        if add_amount:
            try:
                add_amount = int(add_amount)
                x = session['balance'] + add_amount
                cursor.execute("UPDATE User SET Balance = %s WHERE UserID = %s", (x, session['primary']))
                db.commit()
                session['balance'] = x
            except ValueError:
                flash("Invalid amount", "danger")

        cursor.execute("""
            SELECT i.ItemID, i.Name, i.BasePrice, c.Title as Category, 
            a.StartTime, a.EndTime, MAX(B.BidAmount) AS HighestBid
            FROM Item i 
            JOIN Auction a ON i.ItemID = a.ItemID 
            LEFT Join Bid B on a.AuctionID = B.AuctionID AND i.ItemID = B.ItemID
            LEFT JOIN Category c ON i.CategoryID = c.CategoryID WHERE a.EndTime > NOW()
            AND B.BidderID = %s
            GROUP BY i.ItemID, a.AuctionID
        """, (session['primary'],))
        result=cursor.fetchall()
        
        cursor.execute("""SELECT i.ItemID, i.Name, i.BasePrice, c.Title as Category, MAX(B.BidAmount) AS HighestBid FROM Item i JOIN Auction a ON i.ItemID = a.ItemID 
            LEFT Join Bid B on a.AuctionID = B.AuctionID AND i.ItemID = B.ItemID
            LEFT JOIN Category c ON i.CategoryID = c.CategoryID WHERE i.WinnerID = %s
            GROUP BY i.ItemID, a.AuctionID
        """, (session['primary'],))
        result1=cursor.fetchall()
        
        return render_template('bidder_profile.html',items=result, items1=result1) 
    except Error as e:
        flash('Error','danger')
    finally:
        cursor.close()

@app.route('/auctions')
def auctions():
    global db
    cursor = db.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("""
            SELECT i.ItemID, i.Name, i.BasePrice, c.Title as Category, 
            a.StartTime, a.EndTime, MAX(B.BidAmount) AS HighestBid
            FROM Item i 
            JOIN Auction a ON i.ItemID = a.ItemID 
            LEFT Join Bid B on a.AuctionID = B.AuctionID AND i.ItemID = B.ItemID
            LEFT JOIN Category c ON i.CategoryID = c.CategoryID WHERE a.EndTime > NOW()
            GROUP BY i.ItemID, a.AuctionID
        """)
        items = cursor.fetchall()
        for i in items:
            if i['HighestBid'] == None:
                i['HighestBid']= "No bids placed yet"
    finally:
        cursor.close()
    return render_template('auctions.html', items=items,current_page=request.endpoint)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    global db
    cursor = db.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("""SELECT AuctionID from Auction where ItemID = %s AND Auction.EndTime > NOW()""", (item_id,))
        auction = cursor.fetchone()
        if auction is None:
            flash("This item is not available for bidding.", "warning")
            return redirect(url_for('home'))
        auction_id = auction['AuctionID']
        cursor.execute("SELECT * FROM Item WHERE ItemID = %s", (item_id,))
        item = cursor.fetchone()
        cursor.execute("""
            SELECT BidAmount 
            FROM Bid 
            WHERE ItemID = %s AND AuctionID = %s
            ORDER BY BidAmount DESC
            LIMIT 5
        """, (item_id, auction_id))
        bids = cursor.fetchall()
    finally:
        cursor.close()
    return render_template('item_detail.html', item=item, bids=bids)

@app.route('/item1/<int:item_id>')
def item_detail1(item_id):
    global db
    cursor = db.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("""SELECT AuctionID from Auction where ItemID = %s AND Auction.EndTime > NOW()""", (item_id,))
        auction = cursor.fetchone()
        if auction is None:
            cursor.execute("""SELECT * from Item where ItemID = %s""", (item_id,))
            item = cursor.fetchone()
            return render_template('item_detail1.html', item=item, bids = {})
        auction_id = auction['AuctionID']
        cursor.execute("SELECT * FROM Item WHERE ItemID = %s", (item_id,))
        item = cursor.fetchone()
        cursor.execute("""
            SELECT BidAmount 
            FROM Bid 
            WHERE ItemID = %s AND AuctionID = %s
            ORDER BY BidAmount DESC
        """, (item_id, auction_id))
        bids = cursor.fetchall()
    finally:
        cursor.close()
    return render_template('item_detail1.html', item=item, bids=bids)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    global db
    cursor=db.cursor(dictionary=True, buffered=True)
    if request.method=='POST':
        name = request.form['name']
        category = request.form['category']
        base_price = request.form['base_price']
        description = request.form['description']
        image_url=request.form['image_url']
        if ValueError:
            flash("Invalid Base Price", "danger")
            return redirect(url_for('register'))
    try:
        cursor.execute("SELECT CategoryID FROM Category WHERE Title = %s", (category,))
        category_id = cursor.fetchone()
        category_id = category_id['CategoryID']
        cursor.execute("INSERT INTO Item (Name, Description, ImageURL, BasePrice, CategoryID) VALUES (%s,%s,%s,%s,%s)", (name, description, image_url, base_price, category_id))
        db.commit()
        cursor.execute("SELECT ItemID FROM Item WHERE Name = %s AND Description = %s", (name, description))
        item_id = cursor.fetchone()
        item_id1 = item_id['ItemID']
        cursor.execute("INSERT INTO Seller (UserID, ItemID) VALUES (%s,%s)", (session['primary'], item_id1))
        db.commit()
        flash('Item Added Succesfully')
    finally:
        cursor.close()
    return redirect(url_for('seller_profile'))

@app.route('/delete_item/<int:item_id>',methods=['POST'])
def delete_item(item_id):
    global db
    try:
        cursor= db.cursor(dictionary=True, buffered=True)
        cursor.execute("delete from Item where ItemID=%s",(item_id,))
        db.commit()
        flash("Item deleted succesfully","warning")
    except Error as e:
        flash("Client side issue","danger")
    finally:
        cursor.close()
    return redirect(url_for('seller_profile'))
@app.route('/schedule_auction/<int:item_id>', methods=['POST'])
def schedule_auction(item_id):
    global db
    cursor = db.cursor(dictionary=True, buffered=True)

    # Parse and convert
    date_str = request.form['end_time']  # e.g., '2025-04-14T18:30'
    end_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")  # now it's a datetime object
    start_time = datetime.now()
    duration = end_time - start_time  # this is a timedelta
    # Generate next AuctionID
    cursor.execute("SELECT MAX(A.AuctionID) as maxi from Auction A")
    maxi = cursor.fetchone()['maxi']
    new_id = 1 if maxi is None else maxi + 1
    
    # Insert with NOW() for StartTime and Duration as TIMESTAMPDIFF
    cursor.execute("""
        INSERT INTO Auction (AuctionID, ItemID, Duration, StartTime, EndTime)
        VALUES (%s, %s, %s, %s, %s)
    """, (new_id, item_id, duration, start_time, end_time))

    db.commit()
    cursor.close()

    return redirect(url_for('seller_profile'))

@app.route('/bid/<int:item_id>')
def bid(item_id):
    global db
    cursor = db.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("""SELECT AuctionID from Auction where ItemID = %s AND Auction.EndTime > NOW()""", (item_id,))
        auction = cursor.fetchone()
        if auction is None:
            flash("This item is not available for bidding.", "warning")
            return redirect(url_for('home'))
        auction_id = auction['AuctionID']
        cursor.execute("SELECT * FROM Item WHERE ItemID = %s", (item_id,))
        item = cursor.fetchone()
        cursor.execute("""
            SELECT BidderID, BidAmount 
            FROM Bid 
            WHERE ItemID = %s AND AuctionID = %s
            ORDER BY BidAmount DESC Limit 1
        """, (item_id, auction_id))
        bids = cursor.fetchone()
        print(bids)
        if bids["BidderID"] == session['primary']:
            flash("You're already winning this auction!", "warning")
            return redirect(url_for('home'))
        cursor.execute("""SELECT AuctionID from Auction where ItemID = %s AND Auction.EndTime > NOW()""", (item_id,))
        auction = cursor.fetchone()
        if auction is None:
            flash("This item is not available for bidding.", "warning")
            return redirect(url_for('home'))
        
        auction_id = auction['AuctionID']
        cursor.execute("SELECT MAX(BidAmount) FROM Bid WHERE ItemID = %s AND AuctionID = %s", (item_id, auction_id))
        max_bid = cursor.fetchone()
        bidprice=0
        print(max_bid)
        if max_bid['MAX(BidAmount)'] is None:
            cursor.execute('SELECT BasePrice FROM Item WHERE ItemID = %s', (item_id,))
            base_price = cursor.fetchone()
            bidprice = int(base_price['BasePrice'])
        else:
            bidprice = int(11 * (max_bid['MAX(BidAmount)'])/10) 
        if bidprice <= float(session['balance']):
            cursor.execute("Select SUM(HighestBid) as Total from (Select B.BidderID, Max(BidAmount) as HighestBid from Bid AS B JOIN Auction A on B.AuctionID = A.AuctionID and B.ItemID = A.ItemID WHERE A.EndTime > NOW() and B.ItemID != %s GROUP BY A.AuctionID, A.ItemID, B.BidderID HAVING HighestBid = (Select MAX(BidAmount) FROM Bid B1 WHERE B1.AuctionID = A.AuctionID AND B1.ItemID = A.ItemID)) as T where T.BidderID = %s GROUP BY T.BidderID", (item_id, session['primary']))
            result = cursor.fetchone()
            sum = result["Total"] if result else 0
            if(sum + bidprice > session['balance']):
                flash("Bid exceeds your balance, please add more money","warning")
                return redirect(url_for('home')) 
            cursor.execute("SELECT UserID from Seller join Item on Seller.ItemID=Item.ItemID where Item.ItemID=%s",(item_id,))
            result=cursor.fetchone()
            if session['primary']==result['UserID']:
                flash("You can't bid on your own item")
                return redirect(url_for('home'))
            cursor.execute("INSERT INTO Bid (BidderID, AuctionID, ItemID, BidAmount) VALUES (%s, %s, %s, %s)", (session['primary'], auction_id, item_id, bidprice))
            db.commit()
        else:
            flash("Bid exceeds your balance, please add more money","warning")
    except Error as e:
        db.rollback()
        flash(f"Error: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('item_detail',item_id=item_id))

@app.route('/queries')
def queries():
    global db
    return render_template('queries.html',current_page=request.endpoint)

@app.route('/input_query/<int:query_id>', methods=['GET', 'POST'])
def input_query(query_id):
    if query_id == 14:
        if request.method == 'POST':
            auction_id = request.form['auction_id']
            return redirect(url_for('run_query', query_id=query_id, auction_id=auction_id))
        return render_template('query_input.html', query_id=query_id, description=d1[query_id])
    else:
        return redirect(url_for('run_query', query_id=query_id))

def run_query2(query_id):
    global db
    cursor = db.cursor(dictionary=True, buffered=True)
    query = d.get(query_id)

    try:
        if query_id == 14:
            auction_id = request.args.get('auction_id', type=int)
            if not auction_id:
                flash("Auction ID is required for this query.", "warning")
                return redirect(url_for('input_query', query_id=query_id))

            cursor.execute(query, (auction_id,))
        else:
            cursor.execute(query)

        results = cursor.fetchall()
        return render_template('result.html', results=results, description=d1[query_id])
    finally:
        cursor.close()

@app.route('/run_query/<int:query_id>')
def run_query(query_id):
    global db
    query = d.get(query_id)
    cursor=db.cursor(dictionary=True, buffered=True)
    
    try:
        if query_id == 14:
            auction_id = request.args.get('auction_id', type=int)
            if not auction_id:
                #flash("Auction ID is required for this query.", "warning")
                return redirect(url_for('input_query', query_id=query_id))

            cursor.execute(query, (auction_id,))
            rows=cursor.fetchall()
            headers = [description[0] for description in cursor.description]
        else:
            cursor.execute(query)
            rows=cursor.fetchall()
            headers = [description[0] for description in cursor.description]
    finally:
        cursor.close()
    comment=d1[query_id]
    return render_template('result.html',rows=rows, headers=headers, query_id=query_id, comment=comment)

if __name__ == '__main__':
    
    arg1=sys.argv[1]
    arg2=sys.argv[2]
    db=initialize_database()
    if not is_running_from_reloader():
        scheduler.start()
    app.run(debug=True)