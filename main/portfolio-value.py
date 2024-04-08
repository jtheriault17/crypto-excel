import pandas as pd
from datetime import datetime, timedelta
import json
import os.path

def load_portfolio_value():
    portfolio_value = {}
    portfolio_value_path = '../crypto-excel/data/portfolio-value.json'
    if os.path.exists(portfolio_value_path):
        with open(portfolio_value_path, 'r') as f:
            try:
                portfolio_value = json.load(f)
            except json.JSONDecodeError:
                print("Error loading portfolio values. Initializing empty portfolio values.")
    return portfolio_value

def load_portfolio():
    portfolio = {}
    portfolio_path = '../crypto-excel/data/portfolio.json'
    if os.path.exists(portfolio_path):
        with open(portfolio_path, 'r') as f:
            try:
                portfolio = json.load(f)
            except json.JSONDecodeError:
                print("Error loading portfolio. Initializing empty portfolio.")
    return portfolio

def load_cost_basis():
    cost_basis = {}
    cost_basis_path = '../crypto-excel/data/cost_basis.json'
    if os.path.exists(cost_basis_path):
        with open(cost_basis_path, 'r') as f:
            try:
                cost_basis = json.load(f)
            except json.JSONDecodeError:
                print("Error loading cost basis. Initializing empty cost basis.")
    return cost_basis

def load_coin_id_dict():
    coin_id_dict = {}
    coin_id_dict_path = '../crypto-excel/data/coin-id-dictionary.json'
    if os.path.exists(coin_id_dict_path):
        with open(coin_id_dict_path, 'r') as f:
            try:
                coin_id_dict = json.load(f)
            except json.JSONDecodeError:
                print("Error loading coin ID dictionary. Initializing empty dictionary.")
    return coin_id_dict

def get_coin_id(symbol):
    coin_id_dict = load_coin_id_dict()
    return coin_id_dict.get(symbol, None)

# Load historical data from Excel workbook
def load_historical_data(symbol):
    historical_data_path = '../crypto-excel/workbooks/historical-data.xlsx'
    coin_id = get_coin_id(symbol.lower())
    if coin_id is None:
        return {}
    historical_data = pd.read_excel(historical_data_path, sheet_name=coin_id, index_col=0)
    historical_data.index = pd.to_datetime(historical_data.index).date
    historical_data = historical_data.iloc[:, 0].to_dict()
    return historical_data

# Load transactions data from Excel workbook
def load_transaction():
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    transactions = pd.read_excel(workbook_path, sheet_name='Transactions')
    return transactions

# Load total data from Excel workbook
def get_total_data_dates():
    dates = pd.date_range(end=datetime.today(), periods=365, freq = 'D')
    return dates

def get_portfolio(transactions, dates):
    portfolio = load_portfolio()

    portfolio_dates = [datetime.strptime(date_str, '%m/%d/%y') for date_str in portfolio.keys()]

    if portfolio:
        latest_date = max(portfolio_dates)
        latest_date_str = latest_date.strftime('%m/%d/%y')
        del portfolio[latest_date_str]

    for date in dates:
        date_str = date.strftime('%m/%d/%y')
        print(date_str)
        if date_str not in portfolio:
            symbol_data = {}
            for index, row in transactions.iterrows():
                transaction_date = row[0]
                if pd.to_datetime(transaction_date).date() < date.date():
                    received_quantity = row[2] if pd.notna(row[2]) else 0
                    received_currency = row[3] if pd.notna(row[3]) else 0
                    received_cost_basis = row[4] if pd.notna(row[4]) else 0
                    sent_quantity = row[5] if pd.notna(row[5]) else 0
                    sent_currency = row[6] if pd.notna(row[6]) else 0
                    sent_cost_basis = row[7] if pd.notna(row[7]) else 0
                    fee_amount = row[8] if pd.notna(row[8]) else 0
                    fee_currency = row[9] if pd.notna(row[9]) else 0
                    fee_cost_basis = row[10] if pd.notna(row[10]) else 0

                    if received_currency:
                        symbol_data[received_currency] = symbol_data.get(received_currency, {})
                        symbol_data[received_currency]['quantity'] = symbol_data[received_currency].get('quantity', 0) + received_quantity
                        symbol_data[received_currency]['cost_basis'] = symbol_data[received_currency].get('cost_basis', 0) + received_cost_basis
                    if sent_currency:
                        symbol_data[sent_currency] = symbol_data.get(sent_currency, {})
                        symbol_data[sent_currency]['quantity'] = symbol_data[sent_currency].get('quantity', 0) - sent_quantity
                        symbol_data[sent_currency]['cost_basis'] = symbol_data[sent_currency].get('cost_basis', 0) - sent_cost_basis
                    if fee_currency:
                        symbol_data[fee_currency] = symbol_data.get(fee_currency, {})
                        symbol_data[fee_currency]['quantity'] = symbol_data[fee_currency].get('quantity', 0) - fee_amount
                        symbol_data[fee_currency]['cost_basis'] = symbol_data[fee_currency].get('cost_basis', 0) + fee_cost_basis
            # Remove symbols with quantity <= 0 or cost basis <= 1
            symbol_data = {symbol: data for symbol, data in symbol_data.items() if data['quantity'] > 0 and data['cost_basis'] > 1}
            # Calculate value for each symbol using calculate_symbol_value() function
            symbol_values = {}
            for symbol, data in symbol_data.items():
                value = calculate_symbol_value(symbol, data['quantity'], date)
                if value > 0:
                    symbol_values[symbol] = {"quantity": data['quantity'], "value": value, "cost_basis": data['cost_basis']}
            if symbol_values:
                portfolio[date_str] = symbol_values

    with open('../crypto-excel/data/portfolio.json', 'w') as f:
        json.dump(portfolio, f, indent=4)

    return portfolio

# Calculate portfolio value for a given date
def calculate_portfolio_value(date, portfolio):
    portfolio_value = 0
    for symbol, data in portfolio[date].items():
        portfolio_value += data.get('value', 0)
    return portfolio_value

def calculate_symbol_value(symbol, quantity, date):
    historical_data = load_historical_data(symbol)
    if date.date() in historical_data:
        value = quantity * historical_data[date.date()]
        return value
    return 0

def get_portfolio_values(dates, portfolio):
    portfolio_values = load_portfolio_value()

    portfolio_value_dates = [datetime.strptime(date_str, '%m/%d/%y') for date_str in portfolio_values.keys()]

    if portfolio_values:
        latest_date = max(portfolio_value_dates)
        latest_date_str = latest_date.strftime('%m/%d/%y')
        del portfolio_values[latest_date_str]

    for date in dates:
        date_str = date.strftime('%m/%d/%y')
        if date_str not in portfolio_values and date_str in portfolio:
            portfolio_values[date_str] = calculate_portfolio_value(date_str, portfolio)
    with open('../crypto-excel/data/portfolio-value.json', 'w') as f:
                json.dump(portfolio_values, f, indent=4)

    return portfolio_values

def calculate_cost_basis(date, portfolio):
    cost_basis = 0
    for symbol, data in portfolio[date].items():
        cost_basis += data.get('cost_basis', 0)
    return cost_basis

def get_cost_basis(dates, portfolio):
    cost_basis = load_cost_basis()
    
    # Convert date strings to datetime objects for comparison
    cost_basis_dates = [datetime.strptime(date_str, '%m/%d/%y') for date_str in cost_basis.keys()]

    # Delete the latest date entry from cost_basis
    if cost_basis:
        latest_date = max(cost_basis_dates)
        latest_date_str = latest_date.strftime('%m/%d/%y')
        del cost_basis[latest_date_str]
    
    for date in dates:
        date_str = date.strftime('%m/%d/%y')
        if date_str not in cost_basis and date_str in portfolio:
            cost_basis[date_str] = calculate_cost_basis(date_str, portfolio)
    
    with open('../crypto-excel/data/cost-basis.json', 'w') as f:
        json.dump(cost_basis, f, indent=4)

    return cost_basis


def write_values(portfolio_values, cost_basis):
    dates = pd.date_range(end=datetime.today(), periods=len(portfolio_values))
    dates_strs = [date.strftime('%m/%d/%y') for date in dates[::-1]]
    portfolio_df = pd.DataFrame({'Date': dates_strs, 'Portfolio Value': list(portfolio_values.values())[::-1], 'Cost Basis': list(cost_basis.values())[::-1]})
    with pd.ExcelWriter('../crypto-excel/workbooks/total-data.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        portfolio_df.to_excel(writer, sheet_name='Value & Cost Basis', index=False)


def write_portfolio(portfolio):
    portfolio_list = []
    prev_date = None
    for date_str, symbol_values in reversed(list(portfolio.items())):
        for symbol, data in symbol_values.items():
            # Add the date only if it has changed from the previous row
            if date_str != prev_date:
                portfolio_list.append({'Date': date_str, 'Symbol': symbol, 'Quantity': data['quantity'], 'Value': data['value']})
            else:
                portfolio_list.append({'Date': None, 'Symbol': symbol, 'Quantity': data['quantity'], 'Value': data['value']})
            prev_date = date_str

    portfolio_df = pd.DataFrame(portfolio_list)
    
    # Write portfolio data to the 'Total Data' sheet
    with pd.ExcelWriter('../crypto-excel/workbooks/total-data.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        portfolio_df.to_excel(writer, sheet_name='Portfolio', index=False)



# Main function
def main():
    transactions = load_transaction()
    dates = get_total_data_dates()

    portfolio = get_portfolio(transactions, dates)
    portfolio_values = get_portfolio_values(dates, portfolio)
    cost_basis = get_cost_basis(dates, portfolio)

    write_values(portfolio_values, cost_basis)
    write_portfolio(portfolio)


if __name__ == "__main__":
    main()
