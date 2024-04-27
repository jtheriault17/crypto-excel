# Crypto Excel

This project is a tool used to track your crypto portfolio performance and data such as realized/unrealized return, long/short term capital gains/losses, tax estimation, and methods the HIFO, LIFO, FIFO.

## Installation
1. Clone the repository
```bash
   git clone https://github.com/jtheriault17/crypto-excel.git
   ```
2. Install the required dependencies
```bash
   pip install pandas
   ```
```bash
   pip install openpyxl
   ```
```bash
   pip install pypdf2
   ```
```bash
   pip install requests
   ```

## Usage
Note: only have Transactions workbook open, all others shouldn't be touched.

1. Input transactions into Transactions sheet in Transactions.xlsm with most recent transaction at the top of the sheet.
2. If you have any 8949 Forms, then you should use pdf8949.py to update the '8949 Data' sheet. This data will be used to update the Transactions (After Sales).
3. Run main.py.
4. Refresh data in Transactions.xlsm (open Data tab, click Refresh All)
5. If you want to sell some crypto, then use taxes.py. It'll give you tax-loss harvesting data and allow you to see data for selling crypto. You can decide to use HIFO, LIFO, FIFO for each currency, and the script will give you the data you'll need to fill your 8949 Form.
6. Enjoy!

## Acknowledgments

- **Pandas**: Used for data manipulation and analysis.
- **OpenPyXL**: Used for reading and writing Excel files.
- **Python Datetime**: Used for datetime manipulation and formatting.
