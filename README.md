# Binance Home Assignment

The questions that are solved in this assignment:
1. Print the top 5 symbols with quote asset BTC and the highest volume over the last 24 hours in descending order.
2. Print the top 5 symbols with quote asset USDT and the highest number of trades over the last 24 hours in descending order.
3. Using the symbols from Q1, what is the total notional value of the top 200 bids and asks currently on each order book?
4. What is the price spread for each of the symbols from Q2?
5. Every 10 seconds print the result of Q4 and the absolute delta from the previous value for each symbol.
6. Make the output of Q5 accessible by querying http://localhost:8080/metrics using the Prometheus Metrics format.

## Running the tasks

In order to run the code, first install the requirements and then run the .py file:

```bash
pip install -r requirements.txt
python3 tasks.py
```
The code was written and tested on Python 3.9 environment.
