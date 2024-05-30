import pandas as pd
from datetime import datetime, timedelta
import json
import load
import transactions as t

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
    Gets data needed to fill Form 8949 for new SELL transactions.
    """
    currency_data = load.load_currency_data()
    transactions = load.load_transactions_after_sales()
    portfolio = {}
    sell_quantity = {}
    methods = {}

    date_sold = datetime.now().strftime("%m/%d/%y %H:%M:%S")

    for index, row in currency_data.iterrows():
        total_quantity = row[4]
        total_cost_basis = row[7]
        if total_quantity and total_cost_basis:
            currency = row[0]
            price = row[1]

            portfolio[currency] = {}
            portfolio[currency]['Currency'] = currency
            portfolio[currency]['Quantity'] = total_quantity
            portfolio[currency]['Price'] = price
    
    for currency in portfolio:
        choice = float(input(f"\nHow much {currency} would you like to sell? You have {portfolio[currency]['Quantity']} {currency}.\n"))
        while choice > portfolio[currency]['Quantity'] or choice < 0:
            if choice < 0:
                print("\nEnter a valid input. Quantity cannot be negative.")
            else:
                print(f"\nYou don't have enough {currency}. The maximum you can sell is {portfolio[currency]['Quantity']}.")
            choice = float(input(f"How much {currency} would you like to sell? You have {portfolio[currency]['Quantity']} {currency}.\n"))
        sell_quantity[currency] = choice

        hifo = HIFO(transactions, portfolio[currency], sell_quantity[currency], None, date_sold)
        lifo = LIFO(transactions, portfolio[currency], sell_quantity[currency], None, date_sold)
        fifo = FIFO(transactions, portfolio[currency], sell_quantity[currency], None, date_sold)

        if choice != 0:
            choice = input(f"What method would you like to use for {currency} "
                            f"(HIFO = {f'${hifo}' if hifo > 0 else f'-${str(hifo*-1)}'}, "
                            f"LIFO = {f'${lifo}' if lifo > 0 else f'-${str(lifo*-1)}'}, "
                            f"FIFO = {f'${fifo}' if fifo > 0 else f'-${str(fifo*-1)}'})?\n")
        
        while choice not in ['HIFO', 'LIFO', 'FIFO'] and choice:
            print(f"Invalid input. Enter HIFO, LIFO, or FIFO")
            choice = input(f"What method would you like to use for {currency} (HIFO, LIFO, FIFO)?\n")
        methods[currency] = choice

    data = []
    gains = {}
    for currency in portfolio:
        if sell_quantity[currency]:
            if methods[currency] == 'HIFO':
                gains[portfolio[currency]['Currency']] = HIFO(transactions, portfolio[currency], sell_quantity[currency], data, date_sold)
            elif methods[currency] == 'LIFO':
                gains[portfolio[currency]['Currency']] = LIFO(transactions, portfolio[currency], sell_quantity[currency], data, date_sold)
            elif methods[currency] == 'FIFO':
                gains[portfolio[currency]['Currency']] = FIFO(transactions, portfolio[currency], sell_quantity[currency], data, date_sold)
        
    with open('../crypto-excel/data/sell.json', 'w') as f:
        json.dump({}, f, indent=4)
    with open('../crypto-excel/data/sell.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    sum_gains = 0
    for _, value in gains.items():
        sum_gains += value

    return sum_gains

def sold(year, method):
    """
    Description:
    Gets data needed to fill Form 8949 from existing SELL transactions. 
    If filling multiple years of forms, then start from oldest to newest. Transactions need to be updated in the correct order.
    """
    transactions_after_sales = load.load_transactions_after_sales()
    transactions = load.load_transactions()

    transactions['Date'] = pd.to_datetime(transactions['Date'])

    sold_in_year = transactions[transactions['Type'].isin(['SELL', 'TRADE'])]
    sold_in_year = sold_in_year[sold_in_year['Date'].dt.strftime('%Y') == year]
    sold = {}
    for index, row in sold_in_year[::-1].iterrows():
        if row['Sent Currency'] == 'USD':
            continue
        sold[index] = {}
        sold[index]['Date'] = row['Date'].strftime("%m/%d/%y %H:%M:%S")
        sold[index]['Currency'] = row['Sent Currency']
        sold[index]['Quantity'] = row['Sent Quantity']
        sold[index]['Realized Return'] = row['Realized Return (USD)']
        sold[index]['Cost Basis'] = row['Sent Cost Basis (USD)']

        sold[index]['Price'] = (sold[index]['Cost Basis'] + sold[index]['Realized Return']) / sold[index]['Quantity']

    data = []
    gains = 0
    for key, value in sold.items():
        if method == 'HIFO':
            gains += HIFO(transactions_after_sales, value, value['Quantity'], data, value['Date'])
        elif method == 'LIFO':
            gains += LIFO(transactions_after_sales, value, value['Quantity'], data, value['Date'])
        else:
            gains += FIFO(transactions_after_sales, value, value['Quantity'], data, value['Date'])

    with open(f'../crypto-excel/data/sold/sold-{year}.json', 'w') as f:
        json.dump({}, f, indent=4)
    with open(f'../crypto-excel/data/sold/sold-{year}.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    return gains

def HIFO(transactions, currency, sell_quantity, data, date_sold):
    """
    Description:
    Implements Highest-In First-Out method for selling cryptocurrencies.

    Parameters:
    - transactions (dict): Dictionary containing transaction data.
    - currency (dict): Dictionary containing currency sold data.
    - sell_quantity (float): Quantity of currency that was sold.
    - data (dict or None): Dictionary to store selling data.

    Returns:
    float: Total gains from selling.
    """
    gains = 0
    date_sold = datetime.strptime(date_sold, "%m/%d/%y %H:%M:%S")

    hifo_transactions = dict(sorted(transactions.items(), key=lambda x: x[1]['Price'], reverse=True))

    for key, value in hifo_transactions.items():
        if value['Currency'] == currency['Currency'] and sell_quantity:
            date_acquired = datetime.strptime(value['Date'], "%m/%d/%y %H:%M:%S")
            if date_sold < date_acquired:
                continue
            term = 'LONG' if date_sold - date_acquired >= timedelta(days=365) else 'SHORT'
            received_quantity = value['Quantity']
            received_cost_basis = value['Cost Basis']

            if sell_quantity >= received_quantity and received_quantity:
                sell_quantity -= received_quantity
                if data is not None:
                    input = {}

                    input['Currency'] = currency['Currency']
                    input['Quantity'] = received_quantity
                    input['Date Acquired'] = date_acquired.strftime("%m/%d/%y")
                    input['Date Sold'] = date_sold.strftime("%m/%d/%y")
                    input['Proceeds'] = currency['Price'] * received_quantity
                    input['Cost Basis'] = received_cost_basis
                    input['Return'] = input['Proceeds'] - received_cost_basis
                    input['Term'] = term

                    transactions[key]['Quantity'] = 0
                    transactions[key]['Cost Basis'] = 0

                    data.append(input)
                gains +=  (currency['Price'] * received_quantity) - received_cost_basis
            elif received_quantity:
                if data is not None:
                    input = {}

                    input['Currency'] = currency['Currency']
                    input['Quantity'] = sell_quantity
                    input['Date Acquired'] = date_acquired.strftime("%m/%d/%y")
                    input['Date Sold'] = date_sold.strftime("%m/%d/%y")
                    input['Proceeds'] = currency['Price'] * sell_quantity
                    input['Cost Basis'] = (sell_quantity / received_quantity) * received_cost_basis
                    input['Return'] = input['Proceeds'] - input['Cost Basis']
                    input['Term'] = term

                    transactions[key]['Quantity'] -= sell_quantity
                    transactions[key]['Cost Basis'] -= input['Cost Basis']
                   
                    data.append(input)

                gains += (currency['Price'] * sell_quantity) - ((sell_quantity / received_quantity) * received_cost_basis)
                sell_quantity = 0

    return gains
    
def LIFO(transactions, currency, sell_quantity, data, date_sold):
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
    gains = 0
    date_sold = datetime.strptime(date_sold, "%m/%d/%y %H:%M:%S")

    for key, value in transactions.items():
        if value['Currency'] == currency['Currency'] and sell_quantity:
            date_acquired = datetime.strptime(value['Date'], "%m/%d/%y %H:%M:%S")
            if date_sold < date_acquired:
                continue
            term = 'LONG' if date_sold - date_acquired >= timedelta(days=365) else 'SHORT'
            received_quantity = value['Quantity']
            received_cost_basis = value['Cost Basis']

            if sell_quantity > received_quantity:
                sell_quantity -= received_quantity
                if data != None:
                    input = {}

                    input['Currency'] = currency['Currency']
                    input['Quantity'] = received_quantity
                    input['Date Acquired'] = date_acquired.strftime("%m/%d/%y")
                    input['Date Sold'] = date_sold.strftime("%m/%d/%y")
                    input['Proceeds'] = currency['Price'] * received_quantity
                    input['Cost Basis'] = received_cost_basis
                    input['Return'] = input['Proceeds'] - received_cost_basis
                    input['Term'] = term

                    transactions[key]['Quantity'] = 0
                    transactions[key]['Cost Basis'] = 0

                    data.append(input)
                gains +=  (currency['Price'] * received_quantity) - received_cost_basis
            else:
                if data!= None:
                    input = {}

                    input['Currency'] = currency['Currency']
                    input['Quantity'] = sell_quantity
                    input['Date Acquired'] = date_acquired.strftime("%m/%d/%y")
                    input['Date Sold'] = date_sold.strftime("%m/%d/%y")
                    input['Proceeds'] = currency['Price'] * sell_quantity
                    input['Cost Basis'] = (sell_quantity / received_quantity) * received_cost_basis
                    input['Return'] = input['Proceeds'] - input['Cost Basis']
                    input['Term'] = term

                    transactions[key]['Quantity'] -= sell_quantity
                    transactions[key]['Cost Basis'] -=  input['Cost Basis']

                    data.append(input)

                gains += (currency['Price'] * sell_quantity) - ((sell_quantity / received_quantity) * received_cost_basis)
                sell_quantity = 0
    return gains

def FIFO(transactions, currency, sell_quantity, data, date_sold):
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
    gains = 0
    date_sold = datetime.strptime(date_sold, "%m/%d/%y %H:%M:%S")

    for key, value in reversed(transactions.items()):
        if value['Currency'] == currency['Currency'] and sell_quantity:
            date_acquired = datetime.strptime(value['Date'], "%m/%d/%y %H:%M:%S")
            if date_sold < date_acquired:
                continue
            term = 'LONG' if date_sold - date_acquired >= timedelta(days=365) else 'SHORT'
            received_quantity = value['Quantity']
            received_cost_basis = value['Cost Basis']

            if sell_quantity > received_quantity:
                sell_quantity -= received_quantity
                if data != None:
                    input = {}

                    input['Currency'] = currency['Currency']
                    input['Quantity'] = received_quantity
                    input['Date Acquired'] = date_acquired.strftime("%m/%d/%y")
                    input['Date Sold'] = date_sold.strftime("%m/%d/%y")
                    input['Proceeds'] = currency['Price'] * received_quantity
                    input['Cost Basis'] = received_cost_basis
                    input['Return'] = input['Proceeds'] - received_cost_basis
                    input['Term'] = term

                    transactions[key]['Quantity'] = 0
                    transactions[key]['Cost Basis'] = 0

                    data.append(input)
                gains +=  (currency['Price'] * received_quantity) - received_cost_basis
            else:
                if data!= None:
                    input = {}

                    input['Currency'] = currency['Currency']
                    input['Quantity'] = sell_quantity
                    input['Date Acquired'] = date_acquired.strftime("%m/%d/%y")
                    input['Date Sold'] = date_sold.strftime("%m/%d/%y")
                    input['Proceeds'] = currency['Price'] * sell_quantity
                    input['Cost Basis'] = (sell_quantity / received_quantity) * received_cost_basis
                    input['Return'] = input['Proceeds'] - input['Cost Basis']
                    input['Term'] = term

                    transactions[key]['Quantity'] -= sell_quantity
                    transactions[key]['Cost Basis'] -=  input['Cost Basis']

                    data.append(input)

                gains += (currency['Price'] * sell_quantity) - ((sell_quantity / received_quantity) * received_cost_basis)
                sell_quantity = 0
    return gains

# Main function
def main():
    """
    Description:
    Main function to execute tax loss harvesting and selling processes. Use sell if you want to decide method for each transaction. 
    Need to update writing to f8949 for use of sell or update sell, tax_loss_harvesting. Have to manually update it as of now. As of now write_to_f8949 uses sold to write to f8949.
    """
    transactions = load.load_transactions()

    # harvesting, total_loss = tax_loss_harvesting(transactions)
    # print(total_loss)

    with open('../crypto-excel/data/transactions-after-sales.json', 'w') as f:
        json.dump({}, f, indent=4)

    t.update_transactions(transactions, None, None)

    print(f"2021: {sold('2021', 'HIFO')}")
    updated = t.update_transactions(transactions, load.load_f8949('2021'), 'HIFO')
    t.write_to_after_sales(updated)
    
    print(f"2022: {sold('2022', 'HIFO')}")
    updated = t.update_transactions(transactions, load.load_f8949('2022'), 'HIFO')
    t.write_to_after_sales(updated)
    
    print(f"2023: {sold('2023', 'HIFO')}")
    updated = t.update_transactions(transactions, load.load_f8949('2023'), 'HIFO')
    t.write_to_after_sales(updated)

    print(f"2024: {sold('2024', 'HIFO')}")


if __name__ == "__main__":
    main()