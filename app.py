from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os
import sys

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
     10: '''Find users who have participated as both sellers and bidders'''}

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
app.secret_key = "auction_secret"

@app.route('/')
def home():
    return redirect(url_for('auctions'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    global db
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        balance = request.form['balance']

        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO User (Username, Password, Balance) 
                VALUES (%s, %s, %s)
            """, (username, password, balance))
            db.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('auctions'))
        except db.Error as e:
            db.rollback()
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()

    return render_template('register.html')

@app.route('/auctions')
def auctions():
    global db
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT i.ItemID, i.Name, i.BasePrice, c.Title as Category, 
                   a.StartTime, a.EndTime 
            FROM Item i 
            JOIN Auction a ON i.ItemID = a.ItemID 
            LEFT JOIN Category c ON i.CategoryID = c.CategoryID
        """)
        items = cursor.fetchall()
    finally:
        cursor.close()
    return render_template('auctions.html', items=items)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    global db
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Item WHERE ItemID = %s", (item_id,))
        item = cursor.fetchone()
        cursor.execute("""
            SELECT BidAmount 
            FROM Bid 
            WHERE ItemID = %s 
            ORDER BY BidAmount DESC
        """, (item_id,))
        bids = cursor.fetchall()
    finally:
        cursor.close()
    return render_template('item_detail.html', item=item, bids=bids)

@app.route('/queries')
def queries():
    global db
    return render_template('queries.html')

@app.route('/run_query/<int:query_id>')
def run_query(query_id):
    global db
    query = d.get(query_id)
    cursor=db.cursor(dictionary=True)
    try:
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
    app.run(debug=True)