import pandas as pd
from datetime import datetime, timedelta
import json
import os.path
import openpyxl

def load_transaction():
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    transactions = pd.read_excel(workbook_path, sheet_name='Transactions')
    return transactions

def load_8949_data():
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    data_8949 = pd.read_excel(workbook_path, sheet_name='8949 Data')
    return data_8949

def update_transactions(transactions, data):
    sub_cost_basis = {}
    sub_quantity = {}
    updated_transactions = {}

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

    for index, row in transactions.iterrows():
        if row[1] == 'BUY' or row[1] == 'TRADE':
            transaction_date = row[0].strftime('%m/%d/%y')
            received_quantity = row[2] if pd.notna(row[2]) else 0
            received_currency = row[3] if pd.notna(row[3]) else 0
            received_cost_basis = row[4] if pd.notna(row[4]) else 0

            if f'{received_currency} {transaction_date}' not in updated_transactions:
                updated_transactions[f'{received_currency} {transaction_date}'] = {}
                updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] = 0
                updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] = 0

            if received_quantity > sub_quantity.get(f'{received_currency} {transaction_date}', 0) and received_cost_basis > sub_cost_basis.get(f'{received_currency} {transaction_date}', 0):
                updated_transactions[f'{received_currency} {transaction_date}']['Quantity'] += received_quantity - sub_quantity.get(f'{received_currency} {transaction_date}', 0)
                updated_transactions[f'{received_currency} {transaction_date}']['Cost Basis'] += received_cost_basis - sub_cost_basis.get(f'{received_currency} {transaction_date}', 0)
                
                sub_quantity[f'{received_currency} {transaction_date}'] = 0
                sub_cost_basis[f'{received_currency} {transaction_date}'] = 0
            else:
                sub_quantity[f'{received_currency} {transaction_date}'] -= received_quantity
                sub_cost_basis[f'{received_currency} {transaction_date}'] -= received_cost_basis

     # Convert the updated_transactions dictionary to a DataFrame
    df = pd.DataFrame.from_dict(updated_transactions, orient='index')

    # Reset index to split the index into separate columns
    df.reset_index(inplace=True)

    # Split the index into Currency and Date columns
    df[['Currency', 'Date']] = df['index'].str.split(expand=True)

     # Rearrange the columns
    df = df[['Date', 'Currency', 'Quantity', 'Cost Basis']]

    # Remove rows with Quantity or Cost Basis of 0
    df = df[(df['Quantity'] != 0) & (df['Cost Basis'] != 0)]

    return df

def write_to_after_sales(updated_transactions_df):
    # Define the output path
    output_path = '../crypto-excel/workbooks/after-sales.xlsx'

    # Check if the file already exists
    with pd.ExcelWriter(output_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        updated_transactions_df.to_excel(writer, sheet_name='After Sales', index=False)

# Call the function inside main after updating transactions
def main():
    transactions = load_transaction()
    data = load_8949_data()

    updated_transactions_df = update_transactions(transactions, data)

    write_to_after_sales(updated_transactions_df)

if __name__ == "__main__":
    main()