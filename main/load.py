import json
import os.path
import pandas as pd

# -------------------------- JSON ----------------------------------
def load_coin_list():
    coin_list = {}
    if os.path.exists('../crypto-excel/data/coin-list.json'): 
        with open('../crypto-excel/data/coin-list.json', 'r') as f:
            try:
                coin_list = json.load(f)
            except json.JSONDecodeError:
                print("Error loading coin list dictionary. Initializing empty coin list.")
    return coin_list

def load_coin_id_dict():
    coin_id_dict = {}
    if os.path.exists('../crypto-excel/data/coin-id-dictionary.json'):
        with open('../crypto-excel/data/coin-id-dictionary.json', 'r') as f:
            try:
                coin_id_dict = json.load(f)
            except json.JSONDecodeError:
                print("Error loading coin ID dictionary. Initializing empty dictionary.")
    return coin_id_dict

def get_coin_id(symbol):
    coin_id_dict = load_coin_id_dict()
    return coin_id_dict.get(symbol, None)

def load_market_data():
    market_data = {}
    if os.path.exists('../crypto-excel/data/market-data.json'):
        with open ('../crypto-excel/data/market-data.json', 'r') as f:
            try:
                market_data = json.load(f)
            except json.JSONDecodeError:
                print("Error loading market data. Initializing empty market data.")
    return market_data

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
    cost_basis_path = '../crypto-excel/data/cost-basis.json'
    if os.path.exists(cost_basis_path):
        with open(cost_basis_path, 'r') as f:
            try:
                cost_basis = json.load(f)
            except json.JSONDecodeError:
                print("Error loading cost basis. Initializing empty cost basis.")
    return cost_basis

def load_transactions_after_sales():
    transactions = {}
    if os.path.exists('../crypto-excel/data/transactions-after-sales.json'):
        with open('../crypto-excel/data/transactions-after-sales.json', 'r') as f:
            try:
                transactions = json.load(f)
            except json.JSONDecodeError:
                print("Error loading transactions after sales. Initializing transactions after sales.")
    return transactions

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

def load_sell():
    sell = {}
    if os.path.exists('../crypto-excel/data/sell.json'): 
        with open('../crypto-excel/data/sell.json', 'r') as f:
            try:
                coin_list = json.load(f)
            except json.JSONDecodeError:
                print("Error loading sell. Initializing empty sell.")
    return sell

# --------------------------- EXCEL ----------------------------------------------------
def load_historical_data(symbol):
    historical_data_path = '../crypto-excel/workbooks/historical-data.xlsx'
    coin_id = get_coin_id(symbol.lower())
    if coin_id is None:
        return {}
    historical_data = pd.read_excel(historical_data_path, sheet_name=coin_id, index_col=0)
    historical_data.index = pd.to_datetime(historical_data.index).date
    historical_data = historical_data.iloc[:, 0].to_dict()
    return historical_data

def load_transactions():
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    transactions = pd.read_excel(workbook_path, sheet_name='Transactions')
    return transactions

def load_8949_data():
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    data_8949 = pd.read_excel(workbook_path, sheet_name='8949 Data')
    return data_8949

def load_currency_data():
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    data = pd.read_excel(workbook_path, sheet_name='Currency Data')
    return data


