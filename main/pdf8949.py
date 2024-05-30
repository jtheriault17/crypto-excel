import pandas as pd
import camelot
from pdfrw import PdfReader, PdfDict, PdfWriter, PdfName
import load

def read_f8949(paths):
    for year, pdf_path in paths.items():
        dfs = []
        tables = camelot.read_pdf(pdf_path, pages='all')
        for table in tables:
            df = table.df
            df = df.iloc[2:16]
            df = df[df[0] != '']
            fixed_df = {
                'Currency': df[0].str.split().str[-1],
                'Quantity': df[0].str.split().str[0].replace(',', '').astype(float),
                'Date Acquired': df[1],
                'Date Sold': df[2],
                'Proceeds': df[3].str.replace(',', '').astype(float),
                'Cost Basis': df[4].str.replace(',', '').astype(float),
                'Return': df[7].replace({'\(': '-', '\)': '', ',': ''}, regex=True).astype(float)
            }
            dfs.append(pd.DataFrame(fixed_df))

        df = pd.concat(dfs, ignore_index=True)

        df.to_json(f'../crypto-excel/data/f8949/f8949-{str(year)}.json', orient='records', indent=4)

        workbook_path = '../crypto-excel/workbooks/8949Form.xlsx'
        with pd.ExcelWriter(workbook_path, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, sheet_name=str(year), index=False)

def write_to_f8949(year):
    sold = load.load_sold(year)
    shorts = []
    longs = []

    f8949_template = PdfReader(f"../crypto-excel/forms/f8949/{year}/f8949-blank.pdf")
    short_template = f8949_template.pages[0]
    long_template = f8949_template.pages[1]

    for value in sold:
        if value['Term'] == "SHORT":
            new_transaction = {
                'Asset': "{:.8f} {}".format(value['Quantity'], value['Currency']),
                'Date Acquired': value['Date Acquired'],
                'Date Sold': value['Date Sold'],
                'Proceeds': "{:.2f}".format(round(value['Proceeds'], 2)),
                'Cost Basis': "{:.2f}".format(round(value['Cost Basis'], 2)),
                'Empty1': "",
                'Empty2': "",
                'Gain or Loss': "({:.2f})".format(abs(round(value['Return'], 2))) if value['Return'] < 0 else "{:.2f}".format(round(value['Return'],2))
            }
            shorts.append(new_transaction)
        else:
            new_transaction = {
                'Asset': "{:.8f} {}".format(value['Quantity'], value['Currency']),
                'Date Acquired': value['Date Acquired'],
                'Date Sold': value['Date Sold'],
                'Proceeds': "{:.2f}".format(round(value['Proceeds'], 2)),
                'Cost Basis': "{:.2f}".format(round(value['Cost Basis'], 2)),
                'Empty1': "",
                'Empty2': "",
                'Gain or Loss': "({:.2f})".format(abs(round(value['Return'], 2))) if value['Return'] < 0 else "{:.2f}".format(round(value['Return'],2))
            }
            longs.append(new_transaction)
    
    num_long_pages = (len(longs) // 14) + 1
    num_short_pages = (len(shorts) // 14) + 1

    pdf = PdfWriter()
    pdf_path = f'../crypto-excel/forms/f8949/{year}/f8949-filled.pdf'

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
                sums['Gain/Loss'] += float(value.replace('$', '').replace(',', '').replace('(', '-').replace(')', ''))

            sums['Proceeds'] = round(sums['Proceeds'], 2)
            sums['Cost Basis'] = round(sums['Cost Basis'], 2)
            sums['Gain/Loss'] = round(sums['Gain/Loss'], 2)
    return sums

def fill_sum_fields(annotations, sums):
    annotations[-5].update(PdfDict(V='{}'.format(f"{sums['Proceeds']}"), AS='{}'.format(sums['Proceeds'])))
    annotations[-4].update(PdfDict(V='{}'.format(f"{sums['Cost Basis']}"), AS='{}'.format(sums['Cost Basis'])))
    if sums['Gain/Loss'] < 0:
        annotations[-1].update(PdfDict(V=f"({-1 * sums['Gain/Loss']:.2f})", AS=f"{sums['Gain/Loss']:.2f}"))
    else:
        annotations[-1].update(PdfDict(V=f"{sums['Gain/Loss']:.2f}", AS=f"{sums['Gain/Loss']:.2f}"))

def fill_initial_fields(annotations):
    """Fill in the initial fields of the PDF page."""
    annotations[0].update(PdfDict(V='{}'.format("NAME"), AS='{}'.format("NAME")))
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
    # pdf_paths = {}
    # pdf_paths[2021] = '/Users/jimmytheriault/Library/CloudStorage/OneDrive-Personal/Documents/Finance/Taxes/2023/Capital Loss Carryover/2021/Form8949.pdf'
    # pdf_paths[2022] = '/Users/jimmytheriault/Library/CloudStorage/OneDrive-Personal/Documents/Finance/Taxes/2023/Capital Loss Carryover/2022/Form8949.pdf'                
    # pdf_paths[2023] = '/Users/jimmytheriault/Library/CloudStorage/OneDrive-Personal/Documents/Finance/Taxes/2023/Form8949.pdf'

    # read_f8949(pdf_paths)

    years = {2021, 2022, 2023}
    for value in years:
        write_to_f8949(value)

if __name__ == "__main__":
    main()