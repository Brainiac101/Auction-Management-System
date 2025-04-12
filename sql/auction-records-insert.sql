-- use auction;

-- INSERT INTO User (Username, Password, Balance) VALUES
-- ('alice123', 'pass123', 500.00),
-- ('bob456', 'secure456', 300.00),
-- ('charlie789', 'hello789', 800.00),
-- ('david999', 'strong999', 1000.00),
-- ('eve007', 'mypass007', 1200.50),
-- ('frank567', 'test567', 250.00),
-- ('grace888', 'graceful888', 950.00),
-- ('harry321', 'potter321', 600.00),
-- ('isla222', 'secret222', 750.00),
-- ('jack111', 'passjack111', 1100.00);

-- INSERT INTO Category (Title) VALUES
-- ('Electronics'),
-- ('Furniture'),
-- ('Clothing'),
-- ('Books'),
-- ('Sports Equipment'),
-- ('Jewelry'),
-- ('Home Appliances'),
-- ('Toys & Games'),
-- ('Music Instruments'),
-- ('Automobiles'),
-- ('Miscellaneous');

-- INSERT INTO Item (Name, Description, ImageURL, BasePrice, CategoryID, WinnerID) VALUES
-- ('Laptop', 'High-end gaming laptop', 'laptop.jpg', 900.00, 1, NULL),
-- ('Sofa', 'Comfortable 3-seater sofa', 'sofa.jpg', 450.00, 2, NULL),
-- ('T-Shirt', 'Cotton T-shirt', 'tshirt.jpg', 20.00, 3, NULL),
-- ('Novel', 'Best-selling fiction novel', 'novel.jpg', 15.00, 4, NULL),
-- ('Tennis Racket', 'Professional-grade racket', 'racket.jpg', 70.00, 5, NULL),
-- ('Diamond Ring', '18k gold diamond ring', 'ring.jpg', 1500.00, 6, NULL),
-- ('Microwave Oven', '1000W microwave', 'microwave.jpg', 250.00, 7, NULL),
-- ('Board Game', 'Fun family board game', 'boardgame.jpg', 35.00, 8, NULL),
-- ('Car Tires', 'Set of 4 all-season tires', 'tires.jpg', 400.00, 9, NULL),
-- ('Electric Guitar', 'Fender Stratocaster', 'guitar.jpg', 950.00, 10, NULL);

-- INSERT INTO Seller (UserID, ItemID, TotalSales) VALUES
-- (1, 1, 0.00),
-- (2, 2, 0.00),
-- (3, 3, 0.00),
-- (4, 4, 0.00),
-- (5, 5, 0.00),
-- (6, 6, 0.00),
-- (7, 7, 0.00),
-- (8, 8, 0.00),
-- (9, 9, 0.00),
-- (10, 10, 0.00);

-- INSERT INTO Auction (AuctionID, Duration, StartTime, EndTime, ItemID) VALUES
-- (1, '02:00:00', '2025-02-10 14:00:00', '2025-02-10 16:00:00', 1),
-- (2, '03:00:00', '2025-02-11 12:00:00', '2025-02-11 15:00:00', 2),
-- (3, '01:30:00', '2025-02-12 10:30:00', '2025-02-12 12:00:00', 3),
-- (4, '02:45:00', '2025-02-13 15:00:00', '2025-02-13 17:45:00', 4),
-- (5, '04:00:00', '2025-02-14 09:00:00', '2025-02-14 13:00:00', 5),
-- (6, '03:30:00', '2025-02-15 16:00:00', '2025-02-15 19:30:00', 6),
-- (7, '02:00:00', '2025-02-16 18:00:00', '2025-02-16 20:00:00', 7),
-- (8, '05:00:00', '2025-02-17 08:00:00', '2025-02-17 13:00:00', 8),
-- (9, '01:00:00', '2025-02-18 11:00:00', '2025-02-18 12:00:00', 9),
-- (10, '03:15:00', '2025-02-19 14:15:00', '2025-02-19 17:30:00', 10);


-- INSERT INTO Bidder (UserID, AuctionID, ItemID, BidLimit) VALUES
-- (1, 1, 1, 1000.00),
-- (2, 2, 2, 500.00),
-- (3, 3, 3, 50.00),
-- (4, 4, 4, 100.00),
-- (5, 5, 5, 200.00),
-- (6, 6, 6, 2000.00),
-- (7, 7, 7, 300.00),
-- (8, 8, 8, 80.00),
-- (9, 9, 9, 600.00),
-- (10, 1, 1, 120000.00);

-- INSERT INTO Bid (ItemID, AuctionID, BidderID, BidAmount) VALUES
-- (1, 1, 1, 950.00),
-- (2, 2, 2, 480.00),
-- (3, 3, 3, 45.00),
-- (4, 4, 4, 90.00),
-- (5, 5, 5, 150.00),
-- (6, 6, 6, 1800.00),
-- (7, 7, 7, 290.00),
-- (8, 8, 8, 75.00),
-- (9, 9, 9, 580.00),
-- (10, 10, 10, 1100.00);

-- Insert into Bidder values (10, 10, 10, 1200);
-- Insert into Bidder values (10, 2, 2, 1000000);

-- Insert into Bid values (1,1,10,10000.0);
-- Insert into Bid values (2,2,10,10000.0);

use auction; 
-- Insert Users (Both Sellers and Bidders)
INSERT INTO User (Username, Password, Balance) VALUES
('Alice', 'pass123', 1000.00),
('Bob', 'pass123', 500.00),
('Charlie', 'pass123', 750.00),
('David', 'pass123', 1200.00),
('Eve', 'pass123', 300.00),
('Frank', 'pass123', 900.00),
('Grace', 'pass123', 450.00),
('Hank', 'pass123', 800.00),
('Ivy', 'pass123', 1000.00),
('Jack', 'pass123', 600.00);

-- Insert Categories
INSERT INTO Category (Title) VALUES
('Electronics'),
('Furniture'),
('Jewelry'),
('Art'),
('Vehicles');

-- Insert Items
INSERT INTO Item (Name, Description, ImageURL, BasePrice, CategoryID, WinnerID) VALUES
('Laptop', 'A high-performance gaming laptop', 'laptop.jpg', 700.00, 1, NULL),
('Sofa', 'A comfortable leather sofa', 'sofa.jpg', 300.00, 2, NULL),
('Diamond Ring', 'A beautiful diamond ring', 'ring.jpg', 500.00, 3, NULL),
('Painting', 'An exquisite art piece', 'painting.jpg', 200.00, 4, NULL),
('Sports Car', 'A luxurious sports car', 'car.jpg', 5000.00, 5, NULL),
('Smartphone', 'Latest model smartphone', 'phone.jpg', 800.00, 1, NULL),
('Table', 'Wooden dining table', 'table.jpg', 250.00, 2, NULL),
('Gold Necklace', 'Pure gold necklace', 'necklace.jpg', 1000.00, 3, NULL),
('Statue', 'Greek-style marble statue', 'statue.jpg', 350.00, 4, NULL),
('Motorbike', 'Fast and stylish motorbike', 'bike.jpg', 1500.00, 5, NULL);


-- Insert Auctions (Some items are re-auctioned)
INSERT INTO Auction (AuctionID, ItemID, Duration, StartTime, EndTime) VALUES
(1, 1, '02:00:00', '2025-03-01 10:00:00', '2025-03-01 12:00:00'),
(2, 2, '02:30:00', '2025-03-02 14:00:00', '2025-03-02 16:30:00'),
(3, 3, '03:00:00', '2025-03-03 11:00:00', '2025-03-03 14:00:00'),
(4, 4, '02:15:00', '2025-03-04 09:00:00', '2025-03-04 11:15:00'),
(5, 5, '04:00:00', '2025-03-05 15:00:00', '2025-03-05 19:00:00'),
(6, 6, '02:00:00', '2025-03-06 12:00:00', '2025-03-06 14:00:00'),
(7, 7, '01:30:00', '2025-03-07 16:00:00', '2025-03-07 17:30:00'),
(8, 8, '02:45:00', '2025-03-08 10:00:00', '2025-03-08 12:45:00'),
(9, 9, '02:30:00', '2025-03-09 14:30:00', '2025-03-09 17:00:00'),
(10, 10, '03:30:00', '2025-03-10 13:00:00', '2025-03-10 16:30:00'),
(11, 1, '02:00:00', '2025-03-11 10:00:00', '2025-03-11 12:00:00'); -- Re-auctioned

-- Insert Sellers (Some sell multiple items)
INSERT INTO Seller (UserID, ItemID, TotalSales) VALUES
(1, 1, 0.00),
(2, 2, 0.00),
(3, 3, 0.00),
(4, 4, 0.00),
(5, 5, 0.00),
(6, 6, 0.00),
(7, 7, 0.00),
(8, 8, 0.00),
(9, 9, 0.00),
(10, 10, 0.00),
(1, 6, 0.00), -- Alice sells multiple items
(2, 8, 0.00); -- Bob sells multiple items

-- Insert Bidders (Each bids on multiple items)
INSERT INTO Bidder (UserID, AuctionID, ItemID, BidLimit) VALUES
(3, 1, 1, 750.00),
(4, 2, 2, 400.00),
(5, 3, 3, 600.00),
(6, 4, 4, 300.00),
(7, 5, 5, 5500.00),
(8, 6, 6, 900.00),
(9, 7, 7, 350.00),
(10, 8, 8, 1200.00),
(3, 9, 9, 500.00),
(4, 10, 10, 1800.00),
(5, 1, 1, 800.00), -- Multiple bids on the same auction
(6, 5, 5, 6000.00); -- Multiple bids on the same auction

-- Insert Bids
INSERT INTO Bid (ItemID, AuctionID, BidderID, BidAmount) VALUES
(1, 1, 3, 720.00),
(1, 1, 3, 790.00),
(2, 2, 4, 350.00),
(3, 3, 5, 550.00),
(4, 4, 6, 250.00),
(5, 5, 7, 5200.00),
(6, 6, 8, 850.00),
(7, 7, 9, 320.00),
(8, 8, 10, 1150.00),
(9, 9, 3, 450.00),
(10, 10, 4, 1700.00),
(1, 1, 5, 730.00), -- Another bid on same auction
(5, 5, 6, 5700.00); -- Another bid on same auction

-- use auction;
-- select * from Auction;
-- select * from Bid;
-- select * from Bidder;
-- select * from Category;
-- select * from Item;
-- select * from Seller;
-- select * from User;