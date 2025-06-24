# Auction Management System

A web-based auction platform that enables real-time bidding, automatically identifies auction winners using scheduled background tasks, and supports role-based access for admins, sellers, and bidders.

## Functionalities

### User Authentication & Session Management
- Users can sign up or login using a unique username and password.
- A user may be a bidder as well as a seller.
- A seller can add/update items to his/her inventory that can be scheduled for auction at a later time.
- These items can be deleted from the inventory as well.
- Users can see all the auctions currently in progress.
- Users can search for specifc items as well as items from a specific category from the home page.

### Auction Management and Bidding System
- A seller must first schedule an auction, by giving the start and end times, from the list of items available in his/her inventory (available in the top-down menu).
- Once the auction intiates, users can see the auction in the list of available auctions whether logged in or not.
- Bidding on an auction requires for the user to login.
- Users may bid on items based on their wallet balance (available in the top-down menu), which also takes into account the bids that the user has placed on any other auction.
- The bid needs to be atleast 10% higher than the currently winning bid.
- The auction automatically ends when the end time is reached.
- Once the auction finishes, the bidder with the highest bid wins the auction, and is notified of the same. The winner's wallet balance reduces as well.
- If the auction ends with a winner, the seller's wallet balance increases by the winning bid's amount.
- If the auction ends without a winner, the item goes back into the seller's inventory.

### Admin Utilities
- Admin can view various statistics of the platform using his/her own password and id

UserID: `admin`

Password: `admin`

## How to run

> System Requirements:
> - Compatible with Windows, Mac and Linux
> - Python3
> - MySQL


- Go into the project's root directory in the terminal
- Run:

```
pip install -r req.txt
python3 app.py <username> <password>
```

> where the username and the password are the MySQL server details.

- Open `http://127.0.0.1:5000` to view the result

> To terminate the program, run `Ctrl + C` on the terminal.
