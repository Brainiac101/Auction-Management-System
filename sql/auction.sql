drop database if exists auction;
create database if not exists auction;

use auction;
-- Table: User (Superclass)
CREATE TABLE if not exists User (
    UserID INT auto_increment PRIMARY KEY,
    Username VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Balance DECIMAL(10,2 ) NOT NULL CHECK (Balance >= 0),
    CHECK (LENGTH(Username) >= 3)
);

-- Table: Category
CREATE TABLE if not exists Category (
	CategoryID INT auto_increment PRIMARY KEY,
    Title varchar(100) unique
);

-- Table: Item
CREATE TABLE if not exists Item (
    ItemID INT auto_increment PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Description TEXT,
    ImageURL TEXT,
    BasePrice DECIMAL(10,2) NOT NULL CHECK (BasePrice >= 0),
    CategoryID int,
    WinnerID INT,
    FOREIGN KEY (WinnerID) REFERENCES User(UserID) ON DELETE SET NULL,
    FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID) ON DELETE SET NULL
);

-- Table: Auction
CREATE TABLE if not exists Auction (
    AuctionID INT NOT NULL,
    ItemID INT NOT NULL,
    Duration TIME,
    StartTime DATETIME,
    EndTime DATETIME,
    PRIMARY KEY (AuctionID, ItemID),
    FOREIGN KEY (ItemID) REFERENCES Item(ItemID) ON DELETE CASCADE,
    CHECK (StartTime < EndTime)
);

-- Table: Bidder (Weak Entity, Subclass of User)
CREATE TABLE if not exists Bidder (
    UserID INT,
    AuctionID INT,
    ItemID INT,
    BidLimit DECIMAL(10,2) CHECK (BidLimit >= 0),
    PRIMARY KEY (UserID, AuctionID, ItemID),
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (AuctionID, ItemID) REFERENCES Auction(AuctionID, ItemID) ON DELETE CASCADE
);

-- Table: Seller (Subclass of User)
CREATE TABLE if not exists Seller (
    UserID INT,
    ItemID INT,
    TotalSales DECIMAL(10,2) CHECK (TotalSales >= 0),
    PRIMARY KEY (UserID, ItemID),
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (ItemID) REFERENCES Item(ItemID) ON DELETE CASCADE
);

-- Table: Bid
CREATE TABLE if not exists Bid (
    ItemID INT NOT NULL,
    AuctionID INT NOT NULL,
    BidderID INT NOT NULL,
    BidAmount DECIMAL(10,2) NOT NULL CHECK (BidAmount >= 0),
    PRIMARY KEY (BidderID, AuctionID, ItemID, BidAmount),
    CONSTRAINT f2 FOREIGN KEY (AuctionID, ItemID) REFERENCES Auction(AuctionID, ItemID) ON DELETE CASCADE,
    CONSTRAINT f3 FOREIGN KEY (BidderID) REFERENCES User(UserID) ON DELETE CASCADE
);