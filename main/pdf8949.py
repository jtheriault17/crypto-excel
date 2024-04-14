import re
import pandas as pd
import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

import re

# might have to change 8 to 4 since CoinTracker reduced decimals

def parse_8949_text(text):
    text = re.sub(r'(\d+,\d+)', lambda x: x.group(0).replace(',', ''), text)

    currency = re.findall(r'\d+\.\d{8} (\w+)\n', text)
    quantity = [float(x) for x in re.findall(r'(\d+\.\d{8}) \w+\n', text)]
    date_acquired = re.findall(r'(\d{2}/\d{2}/\d{4})\n\d{2}/\d{2}/\d{4}', text)
    date_sold = re.findall(r'\d{2}/\d{2}/\d{4}\n(\d{2}/\d{2}/\d{4})', text)
    proceeds = [float(x) for x in re.findall(r'\n(\d+\.\d{2})\n\d+\.\d{2}\n', text)]
    cost_basis = [float(x) for x in re.findall(r'\n\d+\.\d{2}\n(\d+\.\d{2})\n', text)]

    # Skip every 15th data point
    skip_indices = [i for i in range(14, len(currency), 15)]
    proceeds = [val for i, val in enumerate(proceeds) if i not in skip_indices]
    cost_basis = [val for i, val in enumerate(cost_basis) if i not in skip_indices]

    data = {
        'Currency': currency,
        'Quantity': quantity,
        'Date Acquired': date_acquired,
        'Date Sold': date_sold,
        'Proceeds': proceeds,
        'Cost Basis': cost_basis,
    }

    cut = len(data['Currency']) - len(data['Proceeds'])
    data['Proceeds'] = data['Proceeds'][:cut]
    data['Cost Basis'] = data['Cost Basis'][:cut]

    print(len(data['Proceeds']))
    print(len(data['Currency']))
    print(len(data['Cost Basis']))

    df = pd.DataFrame(data)
    df['Return'] = df['Proceeds'] - df['Cost Basis']
    return df

# Write function to write to 8949 Form eventually


def main():
    pdf_paths = ['/Users/jimmytheriault/Library/CloudStorage/OneDrive-Personal/Documents/Finance/Taxes/2023/Form8949.pdf',
                '/Users/jimmytheriault/Library/CloudStorage/OneDrive-Personal/Documents/Finance/Taxes/2023/Capital Loss Carryover/2022/Form8949.pdf', 
                '/Users/jimmytheriault/Library/CloudStorage/OneDrive-Personal/Documents/Finance/Taxes/2023/Capital Loss Carryover/2021/Form8949.pdf']
    # dfs = []
    # for pdf_path in pdf_paths:
    #     pdf_text = extract_text_from_pdf(pdf_path)
    #     df = parse_8949_text(pdf_text)
    #     dfs.append(df)
    # df = pd.concat(dfs, ignore_index=True)

    # workbook_path = '../crypto-excel/workbooks/Book1.xlsx'
    # sheet_name = '8949'
    # with pd.ExcelWriter(workbook_path, engine='openpyxl', mode='w') as writer:
    #     df.to_excel(writer, sheet_name=sheet_name, index=False)

    pdf_text = extract_text_from_pdf(pdf_paths[0])
    print(pdf_text)
    # df = parse_8949_text(pdf_text)
    # print(df)

if __name__ == "__main__":
    main()