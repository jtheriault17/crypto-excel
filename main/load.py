import json
import os.path
import pandas as pd

# -------------------------- JSON ----------------------------------
def load_coin_list():
    """
    Description:
    Loads the coin list dictionary from a JSON file.

    Returns:
    dict: A dictionary containing coin information, or an empty dictionary if the file doesn't exist or is invalid.
    """
    coin_list = {}
    if os.path.exists('../crypto-excel/data/coin-list.json'): 
        with open('../crypto-excel/data/coin-list.json', 'r') as f:
            try:
                coin_list = json.load(f)
            except json.JSONDecodeError:
                print("Error loading coin list dictionary. Initializing empty coin list.")
    return coin_list

def load_coin_id_dict():
    """
    Description:
    Loads the coin ID dictionary from a JSON file.

    Returns:
    dict: A dictionary containing coin IDs, or an empty dictionary if the file doesn't exist or is invalid.
    """
    coin_id_dict = {}  
    if os.path.exists('../crypto-excel/data/coin-id-dictionary.json'):
        with open('../crypto-excel/data/coin-id-dictionary.json', 'r') as f:
            try:
                coin_id_dict = json.load(f)
            except json.JSONDecodeError:
                print("Error loading coin ID dictionary. Initializing empty dictionary.")
    return coin_id_dict

def get_coin_id(symbol):
    """
    Description:
    Retrieves the coin ID for a given symbol from the loaded coin ID dictionary.

    Parameters:
    - symbol (str): The symbol of the coin.

    Returns:
    str or None: The coin ID if found, or None if not found.
    """
    coin_id_dict = load_coin_id_dict()
    return coin_id_dict.get(symbol, None)

def load_market_data():
    """
    Description:
    Loads market data from a JSON file.

    Returns:
    dict: A dictionary containing market data, or an empty dictionary if the file doesn't exist or is invalid.
    """
    market_data = {}  
    if os.path.exists('../crypto-excel/data/market-data.json'):
        with open ('../crypto-excel/data/market-data.json', 'r') as f:
            try:
                market_data = json.load(f)
            except json.JSONDecodeError:
                print("Error loading market data. Initializing empty market data.")
    return market_data

def load_portfolio_value():
    """
    Description:
    Loads portfolio values from a JSON file.

    Returns:
    dict: A dictionary containing portfolio values, or an empty dictionary if the file doesn't exist or is invalid.
    """
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
    """
    Description:
    Loads portfolio data from a JSON file.

    Returns:
    dict: A dictionary containing portfolio data, or an empty dictionary if the file doesn't exist or is invalid.
    """
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
    """
    Description:
    Loads cost basis data from a JSON file.

    Returns:
    dict: A dictionary containing cost basis data, or an empty dictionary if the file doesn't exist or is invalid.
    """
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
    """
    Description:
    Loads transaction data after sales from a JSON file.

    Returns:
    dict: A dictionary containing transaction data after sales, or an empty dictionary if the file doesn't exist or is invalid.
    """
    transactions = {}  
    if os.path.exists('../crypto-excel/data/transactions-after-sales.json'):
        with open('../crypto-excel/data/transactions-after-sales.json', 'r') as f:
            try:
                transactions = json.load(f)
            except json.JSONDecodeError:
                print("Error loading transactions after sales. Initializing transactions after sales.")
    return transactions

def load_tax_loss_harvesting():
    """
    Description:
    Loads tax loss harvesting data from a JSON file.

    Returns:
    dict: A dictionary containing tax loss harvesting data, or an empty dictionary if the file doesn't exist or is invalid.
    """
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
    """
    Description:
    Loads sell data from a JSON file.

    Returns:
    dict: A dictionary containing sell data, or an empty dictionary if the file doesn't exist or is invalid.
    """
    sell = {}  
    if os.path.exists('../crypto-excel/data/sell.json'): 
        with open('../crypto-excel/data/sell.json', 'r') as f:
            try:
                sell = json.load(f)
            except json.JSONDecodeError:
                print("Error loading sell. Initializing empty sell.")
    return sell

def load_sell():
    """
    Description:
    Loads sold data from a JSON file.

    Returns:
    dict: A dictionary containing sold data, or an empty dictionary if the file doesn't exist or is invalid.
    """
    sold = {}  
    if os.path.exists('../crypto-excel/data/sold.json'): 
        with open('../crypto-excel/data/sold.json', 'r') as f:
            try:
                sold = json.load(f)
            except json.JSONDecodeError:
                print("Error loading sold. Initializing empty sell.")
    return sold

def load_f8949():
    """
    Description:
    Loads f8949 data from a JSON file.

    Returns:
    pandas.DataFrame: A DataFrame containing 8949 data.
    """
    f8949_df = pd.DataFrame() 
    path = '../crypto-excel/data/f8949.json'
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                f8949_data = json.load(f)
                # Convert date strings to datetime objects
                for entry in f8949_data:
                    entry['Date Acquired'] = pd.to_datetime(entry['Date Acquired'], format='%m/%d/%Y')
                    entry['Date Sold'] = pd.to_datetime(entry['Date Sold'], format='%m/%d/%Y')
                # Create DataFrame from the list of dictionaries
                f8949_df = pd.DataFrame(f8949_data)
                # Rename columns to match the desired column names
                f8949_df = f8949_df.rename(columns={
                    'Date Acquired': 'Date Acquired',
                    'Date Sold': 'Date Sold',
                    'Proceeds': 'Proceeds',
                    'Cost Basis': 'Cost Basis',
                    'Return': 'Return'
                })
                # Reorder columns as needed
                f8949_df = f8949_df[['Currency', 'Quantity', 'Date Acquired', 'Date Sold', 'Proceeds', 'Cost Basis', 'Return']]
            except json.JSONDecodeError:
                print("Error loading f8949. Initializing empty f8949.")
    return f8949_df

# --------------------------- EXCEL ----------------------------------------------------
def load_historical_data(symbol):
    """
    Description:
    Loads historical data for a given symbol from an Excel file.

    Parameters:
    - symbol (str): The symbol of the coin.

    Returns:
    dict: A dictionary containing historical data, or an empty dictionary if the coin ID is not found.
    """
    historical_data_path = '../crypto-excel/workbooks/historical-data.xlsx'
    coin_id = get_coin_id(symbol.lower())
    if coin_id is None:
        return {}
    historical_data = pd.read_excel(historical_data_path, sheet_name=coin_id, index_col=0)
    historical_data.index = pd.to_datetime(historical_data.index).date
    historical_data = historical_data.iloc[:, 0].to_dict()
    return historical_data

def load_transactions():
    """
    Description:
    Loads transaction data from an Excel file.

    Returns:
    pandas.DataFrame: A DataFrame containing transaction data.
    """
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    transactions = pd.read_excel(workbook_path, sheet_name='Transactions')
    return transactions

def load_currency_data():
    """
    Description:
    Loads currency data from an Excel file.

    Returns:
    pandas.DataFrame: A DataFrame containing currency data.
    """
    workbook_path = '../crypto-excel/workbooks/Transactions.xlsm'
    data = pd.read_excel(workbook_path, sheet_name='Currency Data')
    return data