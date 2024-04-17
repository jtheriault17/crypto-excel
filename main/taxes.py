import pandas as pd
from datetime import datetime, timedelta
import json
import os.path

def load_tax_loss_harvesting():
    tax_loss_harvesting = {}
    tax_loss_harvesting_path = '../crypto-excel/data/tax-loss-harvesting.json'
    if os.path.exists(tax_loss_harvesting_path):
        with open(tax_loss_harvesting_path, 'r') as f:
            try:
                tax_loss_harvesting = json.load(f)
            except json.JSONDecodeError:
                print("Error loading tax loss harvesting. Initializing empty tax loss harvesting.")
    return tax_loss_harvesting

def load_transactions_after_sales():
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    transactions_after_sales = pd.read_excel(workbook_path, sheet_name='Transactions (After Sales)')
    return transactions_after_sales

def tax_loss_harvesting(transactions):
    tax_loss_harvesting = load_tax_loss_harvesting()
    total_loss = 0
    date_sold = datetime.now().strftime('%m/%d/%y')
    i = 1

    for index, row in transactions.iterrows():
        date_acquired = row[1]
        currency = row[2]
        quantity = row[3]
        cost_basis = row[4]
        current_value = row[6]
        if cost_basis > current_value:
            loss = row[7]
            total_loss += loss
            tax_loss_harvesting[f'{i}'] = {}
            tax_loss_harvesting[f'{i}']['Quantity Sold'] = quantity
            tax_loss_harvesting[f'{i}']['Currency'] = currency
            tax_loss_harvesting[f'{i}']['Date Acquired'] = date_acquired.strftime('%m/%d/%y')
            tax_loss_harvesting[f'{i}']['Date Sold'] = date_sold
            tax_loss_harvesting[f'{i}']['Proceeds'] = current_value
            tax_loss_harvesting[f'{i}']['Cost Basis'] = cost_basis
            tax_loss_harvesting[f'{i}']['Loss'] = loss
            i += 1
    
    with open('../crypto-excel/data/tax-loss-harvesting.json', 'w') as f:
        json.dump(tax_loss_harvesting, f, indent=4)

    return tax_loss_harvesting, total_loss

# Main function
def main():
    transactions = load_transactions_after_sales()

    harvesting, total_loss = tax_loss_harvesting(transactions)

if __name__ == "__main__":
    main()