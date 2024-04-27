import pandas as pd
from datetime import datetime, timedelta
import json
import load

def tax_loss_harvesting(transactions):
    """
    Description:
    Performs tax loss harvesting based on transaction data.

    Parameters:
    - transactions (dict): Dictionary containing transaction data.

    Returns:
    tuple: A tuple containing tax loss harvesting data (dict) and the total loss (float).
    """
    currency_data = load.load_currency_data()
    tax_loss_harvesting = {}
    total_loss = 0
    date_sold = datetime.now().strftime('%m/%d/%y')
    current_prices = {}

    for index, row in currency_data.iterrows():
        currency = row[0]
        current_price = row[1]
        current_prices[currency] = current_price

    for key, value in transactions.items():
        date_acquired = value['Date']
        currency = value['Currency']
        quantity = value['Quantity']
        cost_basis = value['Cost Basis']
        current_value = current_prices[currency] * quantity

        if cost_basis > current_value:
            loss = current_value - cost_basis
            total_loss += loss
            tax_loss_harvesting[key] = {}
            tax_loss_harvesting[key]['Quantity Sold'] = quantity
            tax_loss_harvesting[key]['Currency'] = currency
            tax_loss_harvesting[key]['Date Acquired'] = datetime.strptime(date_acquired, '%m/%d/%y %H:%M:%S').strftime('%m/%d/%y')
            tax_loss_harvesting[key]['Date Sold'] = date_sold
            tax_loss_harvesting[key]['Proceeds'] = current_value
            tax_loss_harvesting[key]['Cost Basis'] = cost_basis
            tax_loss_harvesting[key]['Loss'] = loss

    with open('../crypto-excel/data/tax-loss-harvesting.json', 'w') as f:
        json.dump({}, f, indent=4)
    with open('../crypto-excel/data/tax-loss-harvesting.json', 'w') as f:
        json.dump(tax_loss_harvesting, f, indent=4)

    return tax_loss_harvesting, total_loss

def sell():
    """
    Description:
    Facilitates the selling process for cryptocurrencies.

    Returns:
    dict: Dictionary containing sales data.
    """
    currency_data = load.load_currency_data()
    transactions = load.load_transactions_after_sales()
    portfolio = {}
    sell_quantity = {}
    methods = {}

    for index, row in currency_data.iterrows():
        total_quantity = row[4]
        total_cost_basis = row[7]
        if total_quantity and total_cost_basis:
            currency = row[0]
            price = row[1]

            portfolio[currency] = {}
            portfolio[currency]['Currency'] = currency
            portfolio[currency]['Quantity'] = total_quantity
            portfolio[currency]['Current Price'] = price
    
    for currency in portfolio:
        choice = float(input(f"\nHow much {currency} would you like to sell? You have {portfolio[currency]['Quantity']} {currency}.\n"))
        while choice > portfolio[currency]['Quantity'] or choice < 0:
            if choice < 0:
                print("\nEnter a valid input. Quantity cannot be negative.")
            else:
                print(f"\nYou don't have enough {currency}. The maximum you can sell is {portfolio[currency]['Quantity']}.")
            choice = float(input(f"How much {currency} would you like to sell? You have {portfolio[currency]['Quantity']} {currency}.\n"))
        sell_quantity[currency] = choice

        hifo = HIFO(transactions, portfolio[currency], sell_quantity[currency], None)
        lifo = LIFO(transactions, portfolio[currency], sell_quantity[currency], None)
        fifo = FIFO(transactions, portfolio[currency], sell_quantity[currency], None)

        if choice != 0:
            choice = input(f"What method would you like to use for {currency} "
                            f"(HIFO = {f'${hifo}' if hifo > 0 else f'-${str(hifo*-1)}'}, "
                            f"LIFO = {f'${lifo}' if lifo > 0 else f'-${str(lifo*-1)}'}, "
                            f"FIFO = {f'${fifo}' if fifo > 0 else f'-${str(fifo*-1)}'})?\n")
        
        while choice not in ['HIFO', 'LIFO', 'FIFO'] and choice:
            print(f"Invalid input. Enter HIFO, LIFO, or FIFO")
            choice = input(f"What method would you like to use for {currency} (HIFO, LIFO, FIFO)?\n")
        methods[currency] = choice

    data = {}
    for currency in portfolio:
        if sell_quantity[currency]:
            if methods[currency] == 'HIFO':
                HIFO(transactions, portfolio[currency], sell_quantity[currency], data)
            elif methods[currency] == 'LIFO':
                LIFO(transactions, portfolio[currency], sell_quantity[currency], data)
            elif methods[currency] == 'FIFO':
                FIFO(transactions, portfolio[currency], sell_quantity[currency], data)
        
    with open('../crypto-excel/data/sell.json', 'w') as f:
        json.dump({}, f, indent=4)
    with open('../crypto-excel/data/sell.json', 'w') as f:
        json.dump(data, f, indent=4)

    return data

def HIFO(transactions, currency, sell_quantity, data):
    """
    Description:
    Implements Highest-In First-Out method for selling cryptocurrencies.

    Parameters:
    - transactions (dict): Dictionary containing transaction data.
    - currency (dict): Dictionary containing currency data.
    - sell_quantity (float): Quantity of currency to be sold.
    - data (dict or None): Dictionary to store selling data.

    Returns:
    float: Total gains from selling.
    """
    date_sold = datetime.now().strftime("%m/%d/%y")
    gains = 0

    transactions = dict(sorted(transactions.items(), key=lambda x: x[1]['Price'], reverse=True))

    for key, value in transactions.items():
        if value['Currency'] == currency['Currency'] and sell_quantity:
            date_acquired = datetime.strptime(value['Date'], "%m/%d/%y %H:%M:%S").strftime("%m/%d/%y")
            term = 'LONG' if datetime.strptime(date_sold, "%m/%d/%y") - datetime.strptime(date_acquired, "%m/%d/%y") >= timedelta(days=365) else 'SHORT'
            received_quantity = value['Quantity']
            received_cost_basis = value['Cost Basis']

            if sell_quantity > received_quantity:
                sell_quantity -= received_quantity
                if data != None:
                    data[key] = {}

                    data[key]['Currency'] = currency['Currency']
                    data[key]['Quantity'] = received_quantity
                    data[key]['Date Acquired'] = date_acquired
                    data[key]['Date Sold'] = date_sold
                    data[key]['Proceeds'] = currency['Current Price'] * received_quantity
                    data[key]['Cost Basis'] = received_cost_basis
                    data[key]['Return'] = data[key]['Proceeds'] - received_cost_basis
                    data[key]['Term'] = term

                gains +=  (currency['Current Price'] * received_quantity) - received_cost_basis
            else:
                if data!= None:
                    data[key] = {}

                    data[key]['Currency'] = currency['Currency']
                    data[key]['Quantity'] = sell_quantity
                    data[key]['Date Acquired'] = date_acquired
                    data[key]['Date Sold'] = date_sold
                    data[key]['Proceeds'] = currency['Current Price'] * sell_quantity
                    data[key]['Cost Basis'] = (sell_quantity / received_quantity) * received_cost_basis
                    data[key]['Return'] = data[key]['Proceeds'] - data[key]['Cost Basis']
                    data[key]['Term'] = term
                gains += (currency['Current Price'] * sell_quantity) - ( (sell_quantity / received_quantity) * received_cost_basis)
                sell_quantity = 0
    return gains
    
def LIFO(transactions, currency, sell_quantity, data):
    """
    Description:
    Implements Last-In First-Out method for selling cryptocurrencies.

    Parameters:
    - transactions (dict): Dictionary containing transaction data.
    - currency (dict): Dictionary containing currency data.
    - sell_quantity (float): Quantity of currency to be sold.
    - data (dict or None): Dictionary to store selling data.

    Returns:
    float: Total gains from selling.
    """
    date_sold = datetime.now().strftime("%m/%d/%y")
    gains = 0

    for key, value in transactions.items():
        if value['Currency'] == currency['Currency'] and sell_quantity:
            date_acquired = datetime.strptime(value['Date'], "%m/%d/%y %H:%M:%S").strftime("%m/%d/%y")
            term = 'LONG' if datetime.strptime(date_sold, "%m/%d/%y") - datetime.strptime(date_acquired, "%m/%d/%y") >= timedelta(days=365) else 'SHORT'
            received_quantity = value['Quantity']
            received_cost_basis = value['Cost Basis']

            if sell_quantity > received_quantity:
                sell_quantity -= received_quantity
                if data != None:
                    data[key] = {}

                    data[key]['Currency'] = currency['Currency']
                    data[key]['Quantity'] = received_quantity
                    data[key]['Date Acquired'] = date_acquired
                    data[key]['Date Sold'] = date_sold
                    data[key]['Proceeds'] = currency['Current Price'] * received_quantity
                    data[key]['Cost Basis'] = received_cost_basis
                    data[key]['Return'] = data[key]['Proceeds'] - received_cost_basis
                    data[key]['Term'] = term

                gains +=  (currency['Current Price'] * received_quantity) - received_cost_basis
            else:
                if data!= None:
                    data[key] = {}

                    data[key]['Currency'] = currency['Currency']
                    data[key]['Quantity'] = sell_quantity
                    data[key]['Date Acquired'] = date_acquired
                    data[key]['Date Sold'] = date_sold
                    data[key]['Proceeds'] = currency['Current Price'] * sell_quantity
                    data[key]['Cost Basis'] = (sell_quantity / received_quantity) * received_cost_basis
                    data[key]['Return'] = data[key]['Proceeds'] - data[key]['Cost Basis']
                    data[key]['Term'] = term
                gains += (currency['Current Price'] * sell_quantity) - ( (sell_quantity / received_quantity) * received_cost_basis)
                sell_quantity = 0
    return gains

def FIFO(transactions, currency, sell_quantity, data):
    """
    Description:
    Implements First-In First-Out method for selling cryptocurrencies.

    Parameters:
    - transactions (dict): Dictionary containing transaction data.
    - currency (dict): Dictionary containing currency data.
    - sell_quantity (float): Quantity of currency to be sold.
    - data (dict or None): Dictionary to store selling data.

    Returns:
    float: Total gains from selling.
    """
    date_sold = datetime.now().strftime("%m/%d/%y")
    gains = 0

    for key, value in reversed(transactions.items()):
        if value['Currency'] == currency['Currency'] and sell_quantity:
            date_acquired = datetime.strptime(value['Date'], "%m/%d/%y %H:%M:%S").strftime("%m/%d/%y")
            term = 'LONG' if datetime.strptime(date_sold, "%m/%d/%y") - datetime.strptime(date_acquired, "%m/%d/%y") >= timedelta(days=365) else 'SHORT'
            received_quantity = value['Quantity']
            received_cost_basis = value['Cost Basis']

            if sell_quantity > received_quantity:
                sell_quantity -= received_quantity
                if data != None:
                    data[key] = {}

                    data[key]['Currency'] = currency['Currency']
                    data[key]['Quantity'] = received_quantity
                    data[key]['Date Acquired'] = date_acquired
                    data[key]['Date Sold'] = date_sold
                    data[key]['Proceeds'] = currency['Current Price'] * received_quantity
                    data[key]['Cost Basis'] = received_cost_basis
                    data[key]['Return'] = data[key]['Proceeds'] - received_cost_basis
                    data[key]['Term'] = term

                gains +=  (currency['Current Price'] * received_quantity) - received_cost_basis
            else:
                if data!= None:
                    data[key] = {}

                    data[key]['Currency'] = currency['Currency']
                    data[key]['Quantity'] = sell_quantity
                    data[key]['Date Acquired'] = date_acquired
                    data[key]['Date Sold'] = date_sold
                    data[key]['Proceeds'] = currency['Current Price'] * sell_quantity
                    data[key]['Cost Basis'] = (sell_quantity / received_quantity) * received_cost_basis
                    data[key]['Return'] = data[key]['Proceeds'] - data[key]['Cost Basis']
                    data[key]['Term'] = term
                gains += (currency['Current Price'] * sell_quantity) - ( (sell_quantity / received_quantity) * received_cost_basis)
                sell_quantity = 0
    return gains

# Main function
def main():
    """
    Description:
    Main function to execute tax loss harvesting and selling processes.
    """
    transactions = load.load_transactions_after_sales()

    harvesting, total_loss = tax_loss_harvesting(transactions)

    print(total_loss)

    new_sale = sell()

if __name__ == "__main__":
    main()