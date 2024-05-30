import pandas as pd
from datetime import datetime, timedelta
import json
import load

def get_total_data_dates(date):
    """
    Description:
    Generates a range of dates ending at a specified date.

    Parameters:
    - date (datetime): The end date of the date range.

    Returns:
    pd.DatetimeIndex: A pandas DatetimeIndex object containing the generated dates.
    """
    dates = pd.date_range(end=date, periods=365, freq = 'D')
    return dates

def get_latest_date():
    """
    Description:
    Retrieves the latest date from the portfolio values.

    Returns:
    datetime: The latest date in the portfolio values.
    """
    values = load.load_portfolio_value()
    last_date = max([datetime.strptime(date_str, '%m/%d/%y') for date_str in values.keys()])
    return last_date

def get_portfolio_on_date(transactions, date_str):
    """
    Description:
    Retrieves portfolio data for a specific date.

    Parameters:
    - transactions (pd.DataFrame): DataFrame containing transaction data.
    - date_str (str): Date in string format ('MM/DD/YY').

    Returns:
    dict or None: Portfolio data for the specified date, or None if no data is available.
    """
    portfolio = load.load_portfolio()

    date = datetime.strptime(date_str, '%m/%d/%y')

    if date_str in portfolio.keys():
        return portfolio[date_str]
    else: 
        symbol_data = {}
        for index, row in transactions.iterrows():
            transaction_date = row[0]
            if pd.to_datetime(transaction_date).date() < date.date():
                received_quantity = row[2] if pd.notna(row[2]) else 0
                received_currency = row[3] if pd.notna(row[3]) else 0
                received_cost_basis = row[5] if pd.notna(row[5]) else 0
                sent_quantity = row[6] if pd.notna(row[6]) else 0
                sent_currency = row[7] if pd.notna(row[7]) else 0
                sent_cost_basis = row[8] if pd.notna(row[8]) else 0
                fee_amount = row[9] if pd.notna(row[9]) else 0
                fee_currency = row[10] if pd.notna(row[10]) else 0
                fee_cost_basis = row[11] if pd.notna(row[11]) else 0

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
            return portfolio[date_str]

def get_portfolio(transactions, dates):
    """
    Description:
    Retrieves portfolio data for multiple dates.

    Parameters:
    - transactions (pd.DataFrame): DataFrame containing transaction data.
    - dates (pd.DatetimeIndex): Pandas DatetimeIndex object containing dates.

    Returns:
    dict: Portfolio data for the specified dates.
    """
    portfolio = load.load_portfolio()
    portfolio_dates = [datetime.strptime(date_str, '%m/%d/%y') for date_str in portfolio.keys()]

    if portfolio:
        latest_date = max(portfolio_dates)
        latest_date_str = latest_date.strftime('%m/%d/%y')
        del portfolio[latest_date_str]

    for date in dates:
        date_str = date.strftime('%m/%d/%y')
        if date_str not in portfolio:
            symbol_data = {}
            for index, row in transactions.iterrows():
                transaction_date = row[0]
                if pd.to_datetime(transaction_date).date() < date.date():
                    received_quantity = row[2] if pd.notna(row[2]) else 0
                    received_currency = row[3] if pd.notna(row[3]) else 0
                    received_cost_basis = row[5] if pd.notna(row[5]) else 0
                    sent_quantity = row[6] if pd.notna(row[6]) else 0
                    sent_currency = row[7] if pd.notna(row[7]) else 0
                    sent_cost_basis = row[8] if pd.notna(row[8]) else 0
                    fee_amount = row[9] if pd.notna(row[9]) else 0
                    fee_currency = row[10] if pd.notna(row[10]) else 0
                    fee_cost_basis = row[11] if pd.notna(row[11]) else 0

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

def calculate_portfolio_value(date, portfolio):
    """
    Description:
    Calculates the total value of the portfolio on a specific date.

    Parameters:
    - date (str): Date in string format ('MM/DD/YY').
    - portfolio (dict): Portfolio data for the specified date.

    Returns:
    float: Total value of the portfolio.
    """
    portfolio_value = 0
    for symbol, data in portfolio[date].items():
        portfolio_value += data.get('value', 0)
    return portfolio_value

def calculate_symbol_value(symbol, quantity, date):
    """
    Description:
    Calculates the value of a symbol in the portfolio on a specific date.

    Parameters:
    - symbol (str): Symbol of the cryptocurrency.
    - quantity (float): Quantity of the cryptocurrency.
    - date (datetime): Date of calculation.

    Returns:
    float: Value of the symbol.
    """
    historical_data = load.load_historical_data(symbol)
    
    if date.date() == datetime.now().date():
        market_data = load.load_market_data()
        for coin_data in market_data:
            if coin_data['symbol'].upper() == symbol:
                return coin_data['current_price'] * quantity
    elif date.date() in historical_data:
        value = quantity * historical_data[date.date()]
        return value
    return 0

def get_portfolio_values(dates, portfolio):
    """
    Description:
    Retrieves portfolio values for multiple dates.

    Parameters:
    - dates (pd.DatetimeIndex): Pandas DatetimeIndex object containing dates.
    - portfolio (dict): Portfolio data for the specified dates.

    Returns:
    dict: Portfolio values for the specified dates.
    """
    portfolio_values = load.load_portfolio_value()
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
    """
    Description:
    Calculates the total cost basis of the portfolio on a specific date.

    Parameters:
    - date (str): Date in string format ('MM/DD/YY').
    - portfolio (dict): Portfolio data for the specified date.

    Returns:
    float: Total cost basis of the portfolio.
    """
    cost_basis = 0
    for symbol, data in portfolio[date].items():
        cost_basis += data.get('cost_basis', 0)
    return cost_basis

def get_cost_basis(dates, portfolio):
    """
    Description:
    Retrieves cost basis for multiple dates.

    Parameters:
    - dates (pd.DatetimeIndex): Pandas DatetimeIndex object containing dates.
    - portfolio (dict): Portfolio data for the specified dates.

    Returns:
    dict: Cost basis for the specified dates.
    """
    cost_basis = load.load_cost_basis()
    
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

def write_prices():
    """
    Description:
    Writes current cryptocurrency prices to an Excel file.
    """
    market_data = load.load_market_data()
    current_prices = {}
    for coin_data in market_data:
        symbol = coin_data['symbol'].upper()
        current_price = coin_data['current_price']
        current_prices[symbol] = current_price

    date_str = datetime.today().strftime('%m/%d/%y')

    prices_df = pd.DataFrame({'Symbol': list(current_prices.keys()), 'Price': list(current_prices.values())})

    
    # Write portfolio data to the 'Total Data' sheet
    with pd.ExcelWriter('../crypto-excel/workbooks/total-data.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        prices_df.to_excel(writer, sheet_name='Current Prices', index=False)

def write_values(portfolio_values, cost_basis):
    """
    Description:
    Writes portfolio values and cost basis to an Excel file.

    Parameters:
    - portfolio_values (dict): Portfolio values for the specified dates.
    - cost_basis (dict): Cost basis for the specified dates.
    """
    dates = pd.date_range(end=get_latest_date(), periods=len(portfolio_values))
    dates_strs = [date.strftime('%m/%d/%y') for date in dates[::-1]]

    portfolio_values_list = list(portfolio_values.values())
    cost_basis_list = list(cost_basis.values())
    returns_list = [portfolio_value - cost_basis for portfolio_value, cost_basis in zip(portfolio_values_list, cost_basis_list)]

    portfolio_df = pd.DataFrame({'Date': dates_strs, 'Portfolio Value': portfolio_values_list[::-1], 'Cost Basis': cost_basis_list[::-1], 'Unrealized Return': returns_list[::-1]})
    with pd.ExcelWriter('../crypto-excel/workbooks/total-data.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        portfolio_df.to_excel(writer, sheet_name='Value & Cost Basis', index=False)

def write_portfolio(portfolio):
    """
    Description:
    Writes portfolio data to an Excel file.

    Parameters:
    - portfolio (dict): Portfolio data for the specified dates.
    """
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
    
    # Write portfolio data to the 'Portfolio' sheet
    with pd.ExcelWriter('../crypto-excel/workbooks/total-data.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        portfolio_df.to_excel(writer, sheet_name='Portfolio', index=False)

# ---------------- Main function --------------------
def main():
    """
    Description:
    Main function to execute the portfolio management process.
    """
    transactions = load.load_transactions()
    dates = get_total_data_dates(datetime.today())

    portfolio = get_portfolio(transactions, dates)
    portfolio_values = get_portfolio_values(dates, portfolio)
    cost_basis = get_cost_basis(dates, portfolio)

    write_prices()
    write_values(portfolio_values, cost_basis)
    write_portfolio(portfolio)

if __name__ == "__main__":
    main()
