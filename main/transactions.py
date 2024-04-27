import pandas as pd
from datetime import datetime, timedelta
import json
import os.path
import load

def LIFO(transactions, sub_quantity, sub_cost_basis):
    """
    Description:
    Implements the Last-In First-Out (LIFO) method for updating transactions after sales.

    Parameters:
    - transactions (DataFrame): DataFrame containing transaction data.
    - sub_quantity (dict): Dictionary containing sub-quantity data.
    - sub_cost_basis (dict): Dictionary containing sub-cost basis data.

    Returns:
    dict: Updated transactions after applying the LIFO method.
    """
    updated_transactions = {}
    for index, row in transactions.iterrows():
        if row[1] == 'BUY' or row[1] == 'TRADE':
            seconds = row[0].second
            seconds_rounded = round(seconds, 2)
            seconds_str = str(seconds_rounded).zfill(2)
            transaction_date = row[0].strftime('%m/%d/%y %H:%M:') + seconds_str
            sub_date = row[0].strftime('%m/%d/%y')
            received_quantity = row[2] if pd.notna(row[2]) else 0
            received_currency = row[3] if pd.notna(row[3]) else 0
            price = row[4] if pd.notna(row[4]) else 0
            received_cost_basis = row[5] if pd.notna(row[5]) else 0

            if received_quantity >= sub_quantity.get(f"{received_currency} {sub_date}", 0) and received_cost_basis >= sub_cost_basis.get(f"{received_currency} {sub_date}", 0):
                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Date'] = transaction_date
                updated_transactions[f'{received_currency} {transaction_date}']['Currency'] = received_currency
                updated_transactions[f'{received_currency} {transaction_date}']['Price'] = price
                updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] = received_quantity - sub_quantity.get(f'{received_currency} {sub_date}', 0)
                updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] = received_cost_basis - sub_cost_basis.get(f'{received_currency} {sub_date}', 0)

                sub_quantity[f'{received_currency} {sub_date}'] = 0
                sub_cost_basis[f'{received_currency} {sub_date}'] = 0

                if updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] == 0 or updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] == 0:
                    del updated_transactions[f'{received_currency} {transaction_date}']
            else:
                sub_quantity[f"{received_currency} {sub_date}"] -= received_quantity
                sub_cost_basis[f"{received_currency} {sub_date}"] -= received_cost_basis

    return updated_transactions

def FIFO(transactions, sub_quantity, sub_cost_basis):
    """
    Description:
    Implements the First-In First-Out (FIFO) method for updating transactions after sales.

    Parameters:
    - transactions (DataFrame): DataFrame containing transaction data.
    - sub_quantity (dict): Dictionary containing sub-quantity data.
    - sub_cost_basis (dict): Dictionary containing sub-cost basis data.

    Returns:
    dict: Updated transactions after applying the FIFO method.
    """
    updated_transactions = {}
    for index, row in transactions[::-1].iterrows():
        if row[1] == 'BUY' or row[1] == 'TRADE':
            seconds = row[0].second
            seconds_rounded = round(seconds, 2)
            seconds_str = str(seconds_rounded).zfill(2)
            transaction_date = row[0].strftime('%m/%d/%y %H:%M:') + seconds_str
            sub_date = row[0].strftime('%m/%d/%y')
            received_quantity = row[2] if pd.notna(row[2]) else 0
            received_currency = row[3] if pd.notna(row[3]) else 0
            price = row[4] if pd.notna(row[4]) else 0
            received_cost_basis = row[5] if pd.notna(row[5]) else 0

            if received_quantity >= sub_quantity.get(f"{received_currency} {sub_date}", 0) and received_cost_basis >= sub_cost_basis.get(f"{received_currency} {sub_date}", 0):
                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Date'] = transaction_date
                updated_transactions[f'{received_currency} {transaction_date}']['Currency'] = received_currency
                updated_transactions[f'{received_currency} {transaction_date}']['Price'] = price
                updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] = received_quantity - sub_quantity.get(f'{received_currency} {sub_date}', 0)
                updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] = received_cost_basis - sub_cost_basis.get(f'{received_currency} {sub_date}', 0)

                sub_quantity[f'{received_currency} {sub_date}'] = 0
                sub_cost_basis[f'{received_currency} {sub_date}'] = 0

                if updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] == 0 or updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] == 0:
                    del updated_transactions[f'{received_currency} {transaction_date}']
            else:
                sub_quantity[f"{received_currency} {sub_date}"] -= received_quantity
                sub_cost_basis[f"{received_currency} {sub_date}"] -= received_cost_basis
    
    updated_transactions = dict(sorted(updated_transactions.items(), key=lambda x: datetime.strptime(x[1]['Date'], '%m/%d/%y %H:%M:%S'), reverse=True))
    
    return updated_transactions

def HIFO(transactions, sub_quantity, sub_cost_basis):
    """
    Description:
    Implements the Highest-In First-Out (HIFO) method for updating transactions after sales.

    Parameters:
    - transactions (DataFrame): DataFrame containing transaction data.
    - sub_quantity (dict): Dictionary containing sub-quantity data.
    - sub_cost_basis (dict): Dictionary containing sub-cost basis data.

    Returns:
    dict: Updated transactions after applying the HIFO method.
    """
    updated_transactions = {}

    transactions = transactions.sort_values(by=transactions.columns[4], ascending=False)

    for index, row in transactions.iterrows():
        if row[1] == 'BUY' or row[1] == 'TRADE':
            seconds = row[0].second
            seconds_rounded = round(seconds, 2)
            seconds_str = str(seconds_rounded).zfill(2)
            transaction_date = row[0].strftime('%m/%d/%y %H:%M:') + seconds_str
            sub_date = row[0].strftime('%m/%d/%y')
            received_quantity = row[2] if pd.notna(row[2]) else 0
            received_currency = row[3] if pd.notna(row[3]) else 0
            price = row[4] if pd.notna(row[4]) else 0
            received_cost_basis = row[5] if pd.notna(row[5]) else 0

            if received_quantity >= sub_quantity.get(f"{received_currency} {sub_date}", 0) and received_cost_basis >= sub_cost_basis.get(f"{received_currency} {sub_date}", 0):
                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Date'] = transaction_date
                updated_transactions[f'{received_currency} {transaction_date}']['Currency'] = received_currency
                updated_transactions[f'{received_currency} {transaction_date}']['Price'] = price
                updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] = received_quantity - sub_quantity.get(f'{received_currency} {sub_date}', 0)
                updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] = received_cost_basis - sub_cost_basis.get(f'{received_currency} {sub_date}', 0)

                sub_quantity[f'{received_currency} {sub_date}'] = 0
                sub_cost_basis[f'{received_currency} {sub_date}'] = 0

                if updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] == 0 or updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] == 0:
                    del updated_transactions[f'{received_currency} {transaction_date}']
            else:
                sub_quantity[f"{received_currency} {sub_date}"] -= received_quantity
                sub_cost_basis[f"{received_currency} {sub_date}"] -= received_cost_basis
    
    updated_transactions = dict(sorted(updated_transactions.items(), key=lambda x: datetime.strptime(x[1]['Date'], '%m/%d/%y %H:%M:%S'), reverse=True))
    
    return updated_transactions

def get_sub(data, year):
    """
    Description:
    Retrieves sub-quantity and sub-cost basis data for a specific year.

    Parameters:
    - data (DataFrame): DataFrame containing transaction data.
    - year (int): The year for which data is to be retrieved.

    Returns:
    tuple: A tuple containing sub-quantity and sub-cost basis data (both dictionaries).
    """
    sub_cost_basis = {}
    sub_quantity = {}
    
    filtered_data = data[pd.to_datetime(data.iloc[:, 3]).dt.year == year]

    for index, row in data.iterrows():
        currency = row[0]
        quantity = row[1]
        date_acquired = datetime.strptime(row[2], '%m/%d/%Y').strftime('%m/%d/%y')
        cost_basis = row[5]

        if f'{currency} {date_acquired}' not in sub_cost_basis:
            sub_cost_basis[f'{currency} {date_acquired}'] = 0
        if f'{currency} {date_acquired}' not in sub_quantity:
            sub_quantity[f'{currency} {date_acquired}'] = 0

        sub_cost_basis[f'{currency} {date_acquired}'] += cost_basis
        sub_quantity[f'{currency} {date_acquired}'] += quantity
    
    return sub_quantity, sub_cost_basis

def update_transactions(transactions, data, methods):
    """
    Description:
    Updates transactions after sales using specified methods for different years.

    Parameters:
    - transactions (DataFrame): DataFrame containing transaction data.
    - data (DataFrame): DataFrame containing additional data.
    - methods (dict): Dictionary specifying methods for different years.

    Returns:
    dict: Updated transactions after sales.
    """
    updated_transactions = {}
    
    for method in methods:
        sub_quantity, sub_cost_basis = get_sub(data, method)
        if methods[method] == 'HIFO':
            updated_transactions.update(HIFO(transactions, sub_quantity, sub_cost_basis))
        elif methods[method] == 'LIFO':
            updated_transactions.update(LIFO(transactions, sub_quantity, sub_cost_basis))
        elif methods[method] == 'FIFO':
            updated_transactions.update(HIFO(transactions, sub_quantity, sub_cost_basis))
        
    with open('../crypto-excel/data/transactions-after-sales.json', 'w') as f:
        json.dump({}, f, indent=4)
    with open('../crypto-excel/data/transactions-after-sales.json', 'w') as f:
        json.dump(updated_transactions, f, indent=4)

    return updated_transactions

def write_to_after_sales(updated_transactions):
    """
    Description:
    Writes updated transactions to an Excel file for after-sales data.

    Parameters:
    - updated_transactions (dict): Updated transactions after sales.
    """
    # Define the output path
    output_path = '../crypto-excel/workbooks/after-sales.xlsx'
    df = pd.DataFrame(updated_transactions).T
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y %H:%M:%S')
    # Check if the file already exists
    with pd.ExcelWriter(output_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='After Sales', index=False)

def main():
    """
    Description:
    Main function to update transactions after sales and write them to an Excel file.
    """
    transactions = load.load_transactions()
    data = load.load_8949_data()
    methods = {}
    methods[2021] = 'HIFO'
    methods[2022] = 'HIFO'
    methods[2023] = 'HIFO'

    updated_transactions = update_transactions(transactions, data, methods)

    write_to_after_sales(updated_transactions)

if __name__ == "__main__":
    main()