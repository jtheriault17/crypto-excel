import re
import pandas as pd
import PyPDF2
from pdfrw import PdfReader, PdfDict, PdfWriter, PdfName
import load

def extract_text_from_pdf(pdf_path):
    """
    Description:
    Extracts text from a PDF file.

    Parameters:
    - pdf_path (str): The path to the PDF file.

    Returns:
    str: The extracted text from the PDF.
    """
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

def parse_8949_text(text):
    """
    Description:
    Parses text extracted from a 8949 form PDF.

    Parameters:
    - text (str): The text extracted from the PDF.

    Returns:
    pandas.DataFrame: A DataFrame containing parsed data from the 8949 form.
    """
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

    df = pd.DataFrame(data)
    df['Return'] = df['Proceeds'] - df['Cost Basis']
    return df

# Write function to write to 8949 Form eventually
def write_to_f8949():
    sell = load.load_sell()
    shorts = []
    longs = []

    f8949_template = PdfReader("../crypto-excel/forms/f8949-blank.pdf")
    short_template = f8949_template.pages[0]
    long_template = f8949_template.pages[1]

    for key, value in sell.items():
        if value['Term'] == "SHORT":
            new_transaction = {
                'Asset': "{:.8f} {}".format(value['Quantity'], value['Currency']),
                'Date Acquired': value['Date Acquired'],
                'Date Sold': value['Date Sold'],
                'Proceeds': "{:.8f}".format(value['Proceeds']),
                'Cost Basis': "{:.8f}".format(value['Cost Basis']),
                'Empty1': "",
                'Empty2': "",
                'Gain or Loss': "({:.8f})".format(abs(value['Return'])) if value['Return'] < 0 else "{:.8f}".format(value['Return'])
            }
            shorts.append(new_transaction)
        else:
            new_transaction = {
                'Asset': "{:.8f} {}".format(value['Quantity'], value['Currency']),
                'Date Acquired': value['Date Acquired'],
                'Date Sold': value['Date Sold'],
                'Proceeds': "{:.8f}".format(value['Proceeds']),
                'Cost Basis': "{:.8f}".format(value['Cost Basis']),
                'Empty1': "",
                'Empty2': "",
                'Gain or Loss': "({:.8f})".format(abs(value['Return'])) if value['Return'] < 0 else "{:.8f}".format(value['Return'])
            }
            longs.append(new_transaction)
    
    num_long_pages = (len(longs) // 14) + 1
    num_short_pages = (len(shorts) // 14) + 1

    pdf = PdfWriter()
    pdf_path = '../crypto-excel/forms/f8949-filled.pdf'

    for _ in range(num_short_pages):
        new_page = copy_page(short_template)
        pdf.addPage(new_page)

    for _ in range(num_long_pages):
        new_page = copy_page(long_template)
        pdf.addPage(new_page)

    pdf.write(pdf_path)
    pdf = PdfReader(pdf_path)

    index_offset = 0
    i = 0
    for page in pdf.pages:
        if i < num_short_pages:
            fill_page(page, shorts, index_offset)
        else:
            if i == num_short_pages:
                index_offset = 0
            fill_page(page, longs, index_offset)
        index_offset += 14 * 8
        i += 1

    final_pdf = PdfWriter()
    for page in pdf.pages:
        final_pdf.addPage(page)
    final_pdf.write(pdf_path)

def fill_page(page, data, index_offset):
    sums = {}
    annotations = page['/Annots']

    fill_initial_fields(annotations)
    sums = fill_table(annotations, data, index_offset)
    fill_sum_fields(annotations, sums)

def fill_table(annotations, data, index_offset):
    sums = {}
    sums['Proceeds'] = 0
    sums['Cost Basis'] = 0
    sums['Gain/Loss'] = 0

    keys = ['Asset', 'Date Acquired', 'Date Sold', 'Proceeds', 'Cost Basis', 'Empty1', ' Empty2', 'Gain or Loss']

    for i, annotation in enumerate(annotations[5:-5]):
        i += index_offset
        field_type = annotation['/FT']

        if field_type == '/Tx':
            row = (i // 8)
            col = i % 8

            if row < len(data):
                value = data[row].get(keys[col])
                if value == None:
                    value = ""
            else:
                break
            
            annotation.update(PdfDict(V='{}'.format(value), AS='{}'.format(value)))
            if col == 3:
                sums['Proceeds'] += float(value.replace('$', '').replace(',', ''))
            elif col == 4:
                sums['Cost Basis'] += float(value.replace('$', '').replace(',', ''))
            elif col == 7:
                sums['Gain/Loss'] += float(value.replace('$', '').replace(',', '').replace('(', '').replace(')', ''))

            sums['Proceeds'] = round(sums['Proceeds'], 2)
            sums['Cost Basis'] = round(sums['Cost Basis'], 2)
            sums['Gain/Loss'] = round(sums['Gain/Loss'], 2)
    return sums

def fill_sum_fields(annotations, sums):
    annotations[-5].update(PdfDict(V='{}'.format(f"${sums['Proceeds']}"), AS='{}'.format(sums['Proceeds'])))
    annotations[-4].update(PdfDict(V='{}'.format(f"${sums['Cost Basis']}"), AS='{}'.format(sums['Cost Basis'])))
    annotations[-1].update(PdfDict(V='{}'.format(f"${sums['Gain/Loss']}"), AS='{}'.format(sums['Gain/Loss'])))

def fill_initial_fields(annotations):
    """Fill in the initial fields of the PDF page."""
    annotations[0].update(PdfDict(V='{}'.format("James Theriault"), AS='{}'.format("James Theriault")))
    annotations[1].update(PdfDict(V='{}'.format("123-45-6789"), AS='{}'.format("123-45-6789")))
    annotations[4].update(PdfDict(V=PdfName('On'), AS=PdfName('On')))

def copy_page(page):
    new_page = PdfDict(page)
    if PdfName.Annots in new_page:
        new_page[PdfName.Annots] = [PdfDict(annotation) for annotation in new_page[PdfName.Annots]]
    return new_page

def main():
    """
    Description:
    Main function to execute the parsing of 8949 form PDFs.

    This function currently extracts text from a PDF, parses it, and prints the parsed data.
    """
    pdf_paths = ['/Users/jimmytheriault/Library/CloudStorage/OneDrive-Personal/Documents/Finance/Taxes/2023/Form8949.pdf',
                '/Users/jimmytheriault/Library/CloudStorage/OneDrive-Personal/Documents/Finance/Taxes/2023/Capital Loss Carryover/2022/Form8949.pdf', 
                '/Users/jimmytheriault/Library/CloudStorage/OneDrive-Personal/Documents/Finance/Taxes/2023/Capital Loss Carryover/2021/Form8949.pdf']
    dfs = []
    for pdf_path in pdf_paths:
        pdf_text = extract_text_from_pdf(pdf_path)
        df = parse_8949_text(pdf_text)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)

    workbook_path = '../crypto-excel/workbooks/8949Form.xlsx'
    sheet_name = '8949'
    with pd.ExcelWriter(workbook_path, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    df.to_json('../crypto-excel/data/f8949.json', orient='records', indent=4)

    # Write to f8949 pdf

    write_to_f8949()

if __name__ == "__main__":
    main()