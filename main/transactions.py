import pandas as pd
from datetime import datetime, timedelta
import json
import os.path
import openpyxl

def load_transactions():
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    transactions = pd.read_excel(workbook_path, sheet_name='Transactions')
    return transactions

def load_8949_data():
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    data_8949 = pd.read_excel(workbook_path, sheet_name='8949 Data')
    return data_8949

def load_transactions_after_sales():
    transactions = {}
    if os.path.exists('../crypto-excel/data/transactions-after-sales.json'):
        with open('../crypto-excel/data/transactions-after-sales.json', 'r') as f:
            try:
                transactions = json.load(f)
            except json.JSONDecodeError:
                print("Error loading transactions after sales. Initializing transactions after sales.")
    return transactions

def LIFO(transactions, updated_transactions, sub_quantity, sub_cost_basis):
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
            received_cost_basis = row[5] if pd.notna(row[4]) else 0

            if received_quantity >= sub_quantity.get(f"{received_currency} {sub_date}", 0) and received_cost_basis >= sub_cost_basis.get(f"{received_currency} {sub_date}", 0):
                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Date'] = transaction_date
                updated_transactions[f'{received_currency} {transaction_date}']['Currency'] = received_currency
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

def FIFO(transactions, updated_transactions, sub_quantity, sub_cost_basis):
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
            received_cost_basis = row[5] if pd.notna(row[4]) else 0

            if received_quantity >= sub_quantity.get(f"{received_currency} {sub_date}", 0) and received_cost_basis >= sub_cost_basis.get(f"{received_currency} {sub_date}", 0):
                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Date'] = transaction_date
                updated_transactions[f'{received_currency} {transaction_date}']['Currency'] = received_currency
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

def HIFO(transactions, updated_transactions, sub_quantity, sub_cost_basis):
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
            received_cost_basis = row[5] if pd.notna(row[4]) else 0

            if received_quantity >= sub_quantity.get(f"{received_currency} {sub_date}", 0) and received_cost_basis >= sub_cost_basis.get(f"{received_currency} {sub_date}", 0):
                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Date'] = transaction_date
                updated_transactions[f'{received_currency} {transaction_date}']['Currency'] = received_currency
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
    sub_cost_basis = {}
    sub_quantity = {}
    
    filtered_data = data[pd.to_datetime(data.iloc[:, 3]).dt.year == year]
    print(filtered_data)

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
    updated_transactions = {}
    
    for method in methods:
        sub_quantity, sub_cost_basis = get_sub(data, method)
        if methods[method] == 'HIFO':
            updated_transactions.update(HIFO(transactions, updated_transactions, sub_quantity, sub_cost_basis))
        elif methods[method] == 'LIFO':
            updated_transactions.update(LIFO(transactions, updated_transactions, sub_quantity, sub_cost_basis))
        elif methods[method] == 'FIFO':
            updated_transactions.update(HIFO(transactions, updated_transactions, sub_quantity, sub_cost_basis))
        
    with open('../crypto-excel/data/transactions-after-sales.json', 'w') as f:
        json.dump({}, f, indent=4)
    with open('../crypto-excel/data/transactions-after-sales.json', 'w') as f:
        json.dump(updated_transactions, f, indent=4)

    return updated_transactions

def write_to_after_sales(updated_transactions):
    # Define the output path
    output_path = '../crypto-excel/workbooks/after-sales.xlsx'
    df = pd.DataFrame(updated_transactions).T
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y %H:%M:%S')
    # Check if the file already exists
    with pd.ExcelWriter(output_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='After Sales', index=False)

# Call the function inside main after updating transactions
def main():
    transactions = load_transactions()
    data = load_8949_data()
    methods = {}
    methods[2021] = 'HIFO'
    methods[2022] = 'HIFO'
    methods[2023] = 'HIFO'

    updated_transactions = update_transactions(transactions, data, methods)

    write_to_after_sales(updated_transactions)

if __name__ == "__main__":
    main()