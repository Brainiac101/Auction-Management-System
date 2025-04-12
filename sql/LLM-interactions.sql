-- LLM Interactions

-- FIRST
-- Retrieve all bids for a specific auction along with bidder details
SELECT B.BidderID, U.Username, U.Balance, B.BidAmount, A.AuctionID, I.Name AS ItemName
FROM Bid B
JOIN Bidder BD ON B.BidderID = BD.UserID 
JOIN User U ON BD.UserID = U.UserID
JOIN Auction A ON B.AuctionID = A.AuctionID
JOIN Item I ON A.ItemID = I.ItemID
WHERE B.AuctionID = 1;

-- Fix and Optimisation
SELECT B.BidderID, U.Username, U.Balance, B.BidAmount, B.AuctionID, I.Name AS ItemName
FROM Bid B
JOIN User U ON B.BidderID = U.UserID
JOIN Item I ON B.ItemID = I.ItemID
WHERE B.AuctionID = 1;

-- Alternate Fix
SELECT 
    B.BidderID, 
    U.Username, 
    U.Balance, 
    B.BidAmount, 
    A.AuctionID, 
    I.Name AS ItemName
FROM Bid B
JOIN Bidder BD ON B.BidderID = BD.UserID 
JOIN User U ON BD.UserID = U.UserID
JOIN Auction A ON B.AuctionID = A.AuctionID
JOIN Item I ON A.ItemID = I.ItemID
WHERE B.AuctionID = 1 AND Bd.AuctionID = 1;


-- SECOND
-- Get all bidders who have exceeded their bid limit
SELECT DISTINCT b.UserID, u.Username, b.BidLimit, SUM(bd.BidAmount) AS TotalBidAmount
FROM Bidder b
JOIN User u ON b.UserID = u.UserID
JOIN Bid bd ON b.UserID = bd.BidderID AND b.AuctionID = bd.AuctionID AND b.ItemID = bd.ItemID
GROUP BY b.UserID, u.Username, b.BidLimit
HAVING SUM(bd.BidAmount) > b.BidLimit;

-- FIX:
SELECT
    b.UserID, 
    u.Username, 
    b.BidLimit, 
    bd.BidAmount
FROM Bidder b
JOIN User u ON b.UserID = u.UserID
JOIN Bid bd ON b.UserID = bd.BidderID 
    AND b.AuctionID = bd.AuctionID 
    AND b.ItemID = bd.ItemID
WHERE bd.BidAmount > b.BidLimit;

-- Third
-- Get a list of users and the number of auctions they have participated in (either as a bidder or as a seller)
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
GROUP BY U.UserID, U.Username
ORDER BY U.Username;
-- Error 

-- Fix: Remove ORDER BY clause
USE auction;
SELECT U.Username, COUNT(DISTINCT A.AuctionID) AS NumAuctions
FROM User U
LEFT JOIN Bidder B ON U.UserID = B.UserID
LEFT JOIN Auction A ON B.AuctionID = A.AuctionID
GROUP BY U.UserID, U.Username
UNION ALL
SELECT U.Username, COUNT(DISTINCT A.AuctionID) AS NumAuctions
FROM User U
LEFT JOIN Seller S ON U.UserID = S.UserID
LEFT JOIN Item I ON S.ItemID = I.ItemID
LEFT JOIN Auction A ON I.ItemID = A.ItemID
GROUP BY U.UserID, U.Username
ORDER BY Username;
