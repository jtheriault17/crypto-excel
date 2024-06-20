import pandas as pd
from datetime import datetime
import json
import load

def LIFO(transactions, sub):
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
    updated_transactions = transactions
    for key, value in transactions.items():
        if value['Currency'] == sub['Currency'] and sub['Quantity']:
            transaction_date = value['Date']
            date_acquired = datetime.strptime(transaction_date, '%m/%d/%y %H:%M:%S').strftime('%m/%d/%y')
            if sub['Date Acquired'] != date_acquired:
                continue

            received_quantity = value['Quantity']
            received_currency = value['Currency']
            price = value['Price']
            received_cost_basis = value['Cost Basis']

            if sub['Quantity'] >= received_quantity and received_quantity:
                sub['Quantity'] -= received_quantity
                sub['Cost Basis'] -= received_cost_basis
                del updated_transactions[f'{received_currency} {transaction_date}']
            elif received_quantity:
                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Date'] = transaction_date
                updated_transactions[f'{received_currency} {transaction_date}']['Currency'] = received_currency
                updated_transactions[f'{received_currency} {transaction_date}']['Price'] = price
                updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] = received_quantity - sub['Quantity']
                updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] = received_cost_basis - sub['Cost Basis']

                sub['Quantity'] = 0
                sub['Cost Basis'] = 0

                if updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] == 0 or updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] <= 0.01:
                    del updated_transactions[f'{received_currency} {transaction_date}']
    
    return updated_transactions

def FIFO(transactions, sub):
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
    updated_transactions = transactions
    
    for key, value in reversed(transactions.items()):
        if value['Currency'] == sub['Currency'] and sub['Quantity']:
            transaction_date = value['Date']
            date_acquired = datetime.strptime(transaction_date, '%m/%d/%y %H:%M:%S').strftime('%m/%d/%y')
            if sub['Date Acquired'] != date_acquired:
                continue

            received_quantity = value['Quantity']
            received_currency = value['Currency']
            price = value['Price']
            received_cost_basis = value['Cost Basis']

            if sub['Quantity'] >= received_quantity and received_quantity:
                sub['Quantity'] -= received_quantity
                sub['Cost Basis'] -= received_cost_basis
                del updated_transactions[f'{received_currency} {transaction_date}']
            elif received_quantity:
                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Date'] = transaction_date
                updated_transactions[f'{received_currency} {transaction_date}']['Currency'] = received_currency
                updated_transactions[f'{received_currency} {transaction_date}']['Price'] = price
                updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] = received_quantity - sub['Quantity']
                updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] = received_cost_basis - sub['Cost Basis']

                sub['Quantity'] = 0
                sub['Cost Basis'] = 0

                if updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] == 0 or updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] <= 0.01:
                    del updated_transactions[f'{received_currency} {transaction_date}']
    
    return updated_transactions

def HIFO(transactions, sub):
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
    updated_transactions = transactions.copy()
    transactions = dict(sorted(transactions.items(), key=lambda item: item[1]['Price'], reverse=True))

    for key, value in transactions.items():
        if value['Currency'] == sub['Currency'] and sub['Quantity']:
            transaction_date = value['Date']
            date_acquired = datetime.strptime(transaction_date, '%m/%d/%y %H:%M:%S').strftime('%m/%d/%y')
            if sub['Date Acquired'] != date_acquired:
                continue

            received_quantity = value['Quantity']
            received_currency = value['Currency']
            price = value['Price']
            received_cost_basis = value['Cost Basis']

            if sub['Quantity'] >= received_quantity and received_quantity:
                sub['Quantity'] -= received_quantity
                sub['Cost Basis'] -= received_cost_basis
                del updated_transactions[f'{received_currency} {transaction_date}']
            elif received_quantity:
                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Date'] = transaction_date
                updated_transactions[f'{received_currency} {transaction_date}']['Currency'] = received_currency
                updated_transactions[f'{received_currency} {transaction_date}']['Price'] = price
                updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] = received_quantity - sub['Quantity']
                updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] = received_cost_basis - sub['Cost Basis']

                sub['Quantity'] = 0
                sub['Cost Basis'] = 0

                if updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] == 0 or updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] <= 0.01:
                    del updated_transactions[f'{received_currency} {transaction_date}']
    
    return updated_transactions

def get_sub(data):
    """
    Description:
    Retrieves sub-quantity and sub-cost basis data for a specific year.

    Parameters:
    - data (DataFrame): DataFrame containing transaction data from 8949.

    Returns:
    tuple: A tuple containing sub-quantity and sub-cost basis data (both dictionaries).
    """
    sub = {}

    for index, row in data.iterrows():
        currency = row[0]
        quantity = row[1]
        date_acquired = row[2].strftime('%m/%d/%y')
        date_sold = row[3].strftime('%m/%d/%y')
        proceeds = row[4]
        cost_basis = row[5]
        gains = row[6]

        sub[index] = {}
        sub[index]['Currency'] = currency
        sub[index]['Quantity'] = quantity
        sub[index]['Date Acquired'] = date_acquired
        sub[index]['Date Sold'] = date_sold
        sub[index]['Proceeds'] = proceeds
        sub[index]['Cost Basis'] = cost_basis
        sub[index]['Return'] = gains
    
    return sub

def update_transactions(transactions, data, method):
    """
    Description:
    Updates transactions after sales using specified methods for different years.

    Parameters:
    - transactions (DataFrame): DataFrame containing transaction data.
    - data (DataFrame): DataFrame containing data from 8949.
    - methods (dict): Dictionary specifying methods for different years.

    Returns:
    dict: Updated transactions after sales.
    """
    updated_transactions = load.load_transactions_after_sales()
    
    if method == None or updated_transactions == {}:
        for index, row in transactions.iterrows():
            if row[1] == 'BUY' or row[1] == 'TRADE':
                seconds = row[0].second
                seconds_rounded = round(seconds, 2)
                seconds_str = str(seconds_rounded).zfill(2)
                transaction_date = row[0].strftime('%m/%d/%y %H:%M:') + seconds_str

                received_quantity = row[2] if pd.notna(row[2]) else 0
                received_currency = row[3] if pd.notna(row[3]) else 0
                price = row[4] if pd.notna(row[4]) else 0
                received_cost_basis = row[5] if pd.notna(row[5]) else 0
                fee_cost_basis = row[11] if pd.notna(row[11]) else 0

                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Date'] = transaction_date
                updated_transactions[f'{received_currency} {transaction_date}']['Currency'] = received_currency
                updated_transactions[f'{received_currency} {transaction_date}']['Price'] = price
                updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] = received_quantity
                updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] = received_cost_basis + fee_cost_basis 
    else:
        sub = get_sub(data)
        for key, value in sub.items():
            if method == 'HIFO':
                updated_transactions = HIFO(updated_transactions, value)
            elif method == 'LIFO':
                updated_transactions = LIFO(updated_transactions, value)
            elif method == 'FIFO':
                updated_transactions = FIFO(updated_transactions, value)

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
    # transactions = load.load_transactions()
    # data = load.load_f8949()

    # methods = {}
    # # methods[2021] = 'HIFO'
    # # methods[2022] = 'HIFO'
    # # methods[2023] = 'HIFO'
    # # methods[2024] = 'HIFO'

    # updated_transactions = update_transactions(transactions, data, methods)

    # write_to_after_sales(updated_transactions)

if __name__ == "__main__":
    main()