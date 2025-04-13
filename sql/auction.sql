USE auction;

-- 1. Retrieve all items with their respective category titles
SELECT I.ItemID, I.Name, I.Description, C.Title AS CategoryTitle
FROM Item I
JOIN Category C ON I.CategoryID = C.CategoryID;

-- 2. Get the highest bid for each auction
SELECT A.AuctionID, I.Name AS ItemName, MAX(B.BidAmount) AS HighestBid
FROM Bid B
JOIN Auction A ON B.AuctionID = A.AuctionID
JOIN Item I ON A.ItemID = I.ItemID
GROUP BY A.AuctionID, I.Name;

-- 3. Retrieve the total sales amount for each seller
SELECT S.UserID, U.Username, SUM(S.TotalSales) AS TotalSales
FROM Seller S
JOIN User U ON S.UserID = U.UserID
GROUP BY S.UserID, U.Username
ORDER BY TotalSales DESC;

-- 4. Get all auctions that have ended but have no winner assigned
SELECT A.AuctionID, I.Name AS ItemName, A.EndTime
FROM Auction A
JOIN Item I ON A.ItemID = I.ItemID
WHERE A.EndTime < NOW() AND I.WinnerID IS NULL;

-- 5. Get the top 3 bidders who have placed the highest total bid amount
SELECT B.BidderID, U.Username, SUM(B.BidAmount) AS TotalBidAmount
FROM Bid B
JOIN User U ON B.BidderID = U.UserID
GROUP BY B.BidderID, U.Username
ORDER BY TotalBidAmount DESC
LIMIT 3;

-- 6. Retrieve details of any auction including seller, item, and highest bid
SELECT A.AuctionID, I.Name AS ItemName, U.Username AS Seller, MAX(B.BidAmount) AS HighestBid
FROM Auction A
JOIN Item I ON A.ItemID = I.ItemID
JOIN Seller S ON I.ItemID = S.ItemID
JOIN User U ON S.UserID = U.UserID
LEFT JOIN Bid B ON A.AuctionID = B.AuctionID
GROUP BY A.AuctionID, I.Name, U.Username;

-- 7. Count the number of items in each category
SELECT C.Title AS CategoryTitle, COUNT(I.ItemID) AS ItemCount
FROM Category C
LEFT JOIN Item I ON C.CategoryID = I.CategoryID
GROUP BY C.Title;

-- 8. Get all bidders who have exceeded their bid limit
--SELECT B.UserID, U.Username, B.AuctionID, B.BidLimit, MAX(Bid.BidAmount) AS TotalBids
--FROM Bidder B
--JOIN User U ON B.UserID = U.UserID
--JOIN Bid ON B.UserID = Bid.BidderID
--GROUP BY B.UserID, B.AuctionID, B.ItemID
--HAVING MAX(Bid.BidAmount) > B.BidLimit;

-- 8. Find users who have participated as both sellers and bidders
SELECT DISTINCT U.UserID, U.Username
FROM User U
JOIN Seller S ON U.UserID = S.UserID
JOIN Bidder B ON U.UserID = B.UserID;

-- 9. Find Auctions That Lasted Longer Than the Average Duration
SELECT AuctionID, ItemID, Duration 
FROM Auction 
WHERE Duration > (
    SELECT AVG(Duration) FROM Auction
);

-- 10. Find items that were auctioned more than once
SELECT ItemID, Name 
FROM Item 
WHERE ItemID IN (
    SELECT ItemID 
    FROM Auction 
    GROUP BY ItemID 
    HAVING COUNT(AuctionID) > 1
);

-- 11. Find the Latest auction for each time
SELECT AuctionID, ItemID, StartTime, EndTime 
FROM Auction 
WHERE StartTime = (
    SELECT MAX(StartTime) 
    FROM Auction AS A 
    WHERE A.ItemID = Auction.ItemID
);

-- 12. Find Users Who Have Placed the Most Bids in any Auction 
SELECT UserID, Username 
FROM User 
WHERE UserID IN (
    SELECT BidderID 
    FROM Bid 
    GROUP BY BidderID
    HAVING COUNT(*) = (
        SELECT MAX(BidCount) 
        FROM (
            SELECT COUNT(*) AS BidCount 
            FROM Bid 
            GROUP BY BidderID
        ) AS BidStats
    )
);

-- 13. Find Users Who Have Placed the Most Bids in every Auction
SELECT u.UserID, u.Username, b.AuctionID, COUNT(b.BidAmount) AS TotalBids
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
);
