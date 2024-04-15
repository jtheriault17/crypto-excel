from fetch_write_data import main as fetch_write_data_main
from portfolio import main as portfolio_main
from transactions import main as transactions_main

def main():
    # Run fetch_write_data.py
    fetch_write_data_main()

    # Run portfolio.py
    portfolio_main()

    # Run transactions.py
    transactions_main()

if __name__ == "__main__":
    main()
