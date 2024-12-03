import pandas as pd
from datetime import datetime, date
import load

def is_valid_currency(currency, valid_currencies):
    return currency in valid_currencies

def is_valid_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_valid_date(date_string):
    try:
        # Check if time is provided
        if len(date_string.split()) == 1:
            date_string += " 00:00:00"
        dt = datetime.strptime(date_string, "%m/%d/%Y %H:%M:%S")
        # Check if the date is in the future
        if dt.date() > date.today():
            return False
        return True
    except ValueError:
        return False

def add_transaction():
    coin_list = load.load_coin_list()
    valid_currencies = {coin['symbol'].upper() for coin in coin_list}
    valid_currencies.add('USD')

    date = input("Enter transaction's date (mm/dd/yyy h:m:s):")
    while not is_valid_date(date):
        print("Invalid date format. Please enter in the format mm/dd/yyyy h:m:s.")
        date = input("Enter transaction's date (mm/dd/yyyy h:m:s):")

    type = input("Enter transaction's type (BUY, SELL, TRANSFER):").upper()
    while type not in {'BUY', 'SELL', 'TRANSFER'}:
        print("Invalid transaction type. Please enter 'BUY', 'SELL', or 'TRANSFER'.")
        type = input("Enter transaction's type (BUY, SELL, TRANSFER):").upper()

    if type == 'BUY':
        received_quantity = input("Enter transaction's received quantity:")
        while not is_valid_number(received_quantity):
            print("Invalid quantity. Please enter a number.")
            received_quantity = input("Enter transaction's received quantity:")

        received_cost_basis = input("Enter transaction's received cost basis (USD):")
        while not is_valid_number(received_cost_basis):
            print("Invalid cost basis. Please enter a number.")
            received_cost_basis = input("Enter transaction's received cost basis (USD):")

        received_currency = input("Enter transaction's received currency:").upper()
        while not is_valid_currency(received_currency, valid_currencies):
            print("Invalid currency ticker. Please enter a valid ticker (e.g., BTC, ETH).")
            received_currency = input("Enter transaction's received currency:").upper()
    
    elif type == 'SELL':
        sent_quantity = input("Enter transaction's sent quantity:")
        while not is_valid_number(sent_quantity):
            print("Invalid quantity. Please enter a number.")
            sent_quantity = input("Enter transaction's sent quantity:")

        sent_cost_basis = input("Enter transaction's sent cost basis (USD):")
        while not is_valid_number(sent_cost_basis):
            print("Invalid cost basis. Please enter a number.")
            sent_cost_basis = input("Enter transaction's sent cost basis (USD):")

        sent_currency = input("Enter transaction's sent currency:").upper()
        while not is_valid_currency(sent_currency, valid_currencies):
            print("Invalid currency ticker. Please enter a valid ticker (e.g., BTC, ETH).")
            sent_currency = input("Enter transaction's sent currency:").upper()

    else:
        received_quantity = input("Enter transaction's received quantity:")
        while not is_valid_number(received_quantity):
            print("Invalid quantity. Please enter a number.")
            received_quantity = input("Enter transaction's received quantity:")

        received_cost_basis = input("Enter transaction's received cost basis (USD):")
        while not is_valid_number(received_cost_basis):
            print("Invalid cost basis. Please enter a number.")
            received_cost_basis = input("Enter transaction's received cost basis (USD):")

        received_currency = input("Enter transaction's received currency:").upper()
        while not is_valid_currency(received_currency, valid_currencies):
            print("Invalid currency ticker. Please enter a valid ticker (e.g., BTC, ETH).")
            received_currency = input("Enter transaction's received currency:").upper()

        sent_quantity = input("Enter transaction's sent quantity:")
        while not is_valid_number(sent_quantity):
            print("Invalid quantity. Please enter a number.")
            sent_quantity = input("Enter transaction's sent quantity:")

        sent_cost_basis = input("Enter transaction's sent cost basis (USD):")
        while not is_valid_number(sent_cost_basis):
            print("Invalid cost basis. Please enter a number.")
            sent_cost_basis = input("Enter transaction's sent cost basis (USD):")

        sent_currency = input("Enter transaction's sent currency:").upper()
        while not is_valid_currency(sent_currency, valid_currencies):
            print("Invalid currency ticker. Please enter a valid ticker (e.g., BTC, ETH).")
            sent_currency = input("Enter transaction's sent currency:").upper()

    fee_amount = input("Enter transaction's fee amount:")
    while not is_valid_number(fee_amount):
        print("Invalid fee amount. Please enter a number.")
        fee_amount = input("Enter transaction's fee amount:")

    fee_currency = input("Enter transaction's fee currency:").upper()
    while not is_valid_currency(fee_currency, valid_currencies):
        print("Invalid currency ticker. Please enter a valid ticker (e.g., BTC, ETH).")
        fee_currency = input("Enter transaction's fee currency:").upper()

    fee_cost_basis = input("Enter transaction's fee cost basis (USD):")
    while not is_valid_number(fee_cost_basis):
        print("Invalid cost basis. Please enter a number.")
        fee_cost_basis = input("Enter transaction's fee cost basis (USD):")

def open_csv(path):
    try:
        df = pd.read_csv(path, skiprows=3)
    except pd.errors.ParserError as e:
        df = f"ParserError: {e}"
    except Exception as e:
        df = f"An error occurred: {e}"
    return df

def import_coinbase_transactions(path):
    df = open_csv(path)
    # Filter out deposits and staking income
    df_filtered = df[~df['Transaction Type'].isin(['Deposit', 'Staking Income'])]

    # Define the mapping for transaction types
    transaction_type_mapping = {
        'Receive': 'TRANSFER',
        'Send': 'TRANSFER',
        'Buy': 'BUY',
        'Sell': 'SELL',
        'Convert': 'TRADE',
        'Withdrawal': 'SELL'
    }

    # Apply the transaction type mapping
    df_filtered['Transaction Type'] = df_filtered['Transaction Type'].map(transaction_type_mapping)

    # Convert timestamps to the new format
    df_filtered['Timestamp'] = pd.to_datetime(df_filtered['Timestamp']).dt.strftime('%m/%d/%y %H:%M:%S')

    # Initialize the new DataFrame structure
    new_df = pd.DataFrame({
        'Date': df_filtered['Timestamp'],
        'Type': df_filtered['Transaction Type'],
        'Received Quantity': None,
        'Received Currency': None,
        'Price (estimated)': df_filtered['Price at Transaction'],
        'Received Cost Basis (USD)': None,
        'Sent Quantity': None,
        'Sent Currency': None,
        'Sent Cost Basis (USD)': None,
        'Fee Amount': df_filtered['Fees and/or Spread'],
        'Fee Currency': 'USD',  # Set Fee Currency to USD
        'Fee Cost Basis (USD)': df_filtered['Fees and/or Spread'],
        'Realized Return (USD)': df_filtered['Total (inclusive of fees and/or spread)'],
        'Fee Realized Return (USD)': None
    })

    # Fill in the appropriate columns based on transaction type
    for index, row in df_filtered.iterrows():
        transaction_type = row['Transaction Type']
        
        if transaction_type in ['BUY', 'TRANSFER']:
            new_df.at[index, 'Received Quantity'] = row['Quantity Transacted']
            new_df.at[index, 'Received Currency'] = row['Asset']
            new_df.at[index, 'Received Cost Basis (USD)'] = row['Subtotal']
        elif transaction_type in ['SELL']:
            new_df.at[index, 'Sent Quantity'] = row['Quantity Transacted']
            new_df.at[index, 'Sent Currency'] = row['Asset']
            new_df.at[index, 'Sent Cost Basis (USD)'] = row['Subtotal']
        elif transaction_type == 'TRADE':
            notes = row['Notes']
            if notes:
                parts = notes.split(' ')
                if len(parts) >= 7:
                    sent_quantity = parts[1]
                    sent_currency = parts[2]
                    received_quantity = parts[5]
                    received_currency = parts[6]
                    new_df.at[index, 'Received Quantity'] = received_quantity
                    new_df.at[index, 'Received Currency'] = received_currency
                    new_df.at[index, 'Sent Quantity'] = sent_quantity
                    new_df.at[index, 'Sent Currency'] = sent_currency
                    new_df.at[index, 'Received Cost Basis (USD)'] = row['Subtotal']
                    new_df.at[index, 'Sent Cost Basis (USD)'] = row['Subtotal']
    
    print(new_df)

    # # Save the final DataFrame to a JSON file
    # final_json_path = 'path/to/save/converted_transactions.json'
    # new_df.to_json(final_json_path, orient='records', date_format='iso')

    # # Output the path to the saved JSON file
    # print(final_json_path)

def main():
    # add_transaction()
    import_coinbase_transactions('../crypto-excel/data/transactions/coinbase_transactions.csv')

if __name__ == "__main__":
    main()