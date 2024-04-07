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
    historical_data.index = pd.to_datetime(historical_data.index)
    historical_data = historical_data.squeeze().to_dict()
    return historical_data

# Load transactions data from Excel workbook
def load_transaction():
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    transactions = pd.read_excel(workbook_path, sheet_name='Transactions')
    return transactions

# Load total data from Excel workbook
def get_total_data_dates():
    end_date = datetime.today() - timedelta(days=365)
    dates = pd.date_range(end=end_date, periods=365)
    return dates

def get_cost_basis(transactions, dates):
    cost_basis = load_cost_basis()
    for date in dates:
        date_str = date.strftime('%m/%d/%y')

def get_portfolio(transactions, dates):
    portfolio = load_portfolio()
    for date in dates:
        date_str = date.strftime('%m/%d/%y')
        if date_str not in portfolio:
            symbol_data = {}
            for index, row in transactions.iterrows():
                transaction_date = row[0]
                if pd.to_datetime(transaction_date).date() < date.date():
                    received_quantity = row[2].fillna(0)
                    received_currency = row[3].fillna(0)
                    received_cost_basis = row[4].fillna(0)
                    sent_quantity = row[5].fillna(0)
                    sent_currency = row[6].fillna(0)
                    sent_cost_basis = row[7].fillna(0)
                    fee_amount = row[8].fillna(0)
                    fee_currency = row[9].fillna(0)
                    fee_cost_basis = row[10].fillna(0)

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
            # Remove symbols with quantity <= 0
            symbol_data = {symbol: data for symbol, data in symbol_data.items() if data['quantity'] > 0}
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
    for date in dates:
        date_str = date.strftime('%m/%d/%y')
        if date_str not in portfolio_values:
            portfolio_values[date_str] = calculate_portfolio_value(date_str, portfolio)
    with open('../crypto-excel/data/portfolio-value.json', 'w') as f:
                json.dump(portfolio_values, f, indent=4)

    return portfolio_values

def write_portfolio_values(portfolio_values):
    dates = pd.date_range(end=datetime.today(), periods=len(portfolio_values))
    portfolio_df = pd.DataFrame({'Date': dates, 'Portfolio Value': list(portfolio_values.values())})
    portfolio_df.to_excel('../crypto-excel/workbooks/total-data.xlsx', index=False)

def write_portfolio(portfolio):
    portfolio_list = []
    for date_str, symbol_values in portfolio.items():
        for symbol, data in symbol_values.items():
            portfolio_list.append({'Date': date_str, 'Symbol': symbol, 'Quantity': data['quantity'], 'Value': data['value']})

    portfolio_df = pd.DataFrame(portfolio_list)
    
    # Write portfolio data to the 'Total Data' sheet
    with pd.ExcelWriter('../crypto-excel/workbooks/total-data.xlsx', mode='a', engine='openpyxl') as writer:
        portfolio_df.to_excel(writer, sheet_name='Total Data', index=False)


# Main function
def main():
    transactions = load_transaction()
    dates = get_total_data_dates()

    portfolio = get_portfolio(transactions, dates)
    portfolio_values = get_portfolio_values(dates, portfolio)

    write_portfolio_values(portfolio_values)
    write_portfolio(portfolio)

    # print(os.listdir('../crypto-excel/crypto-excel/workbooks'))


if __name__ == "__main__":
    main()
