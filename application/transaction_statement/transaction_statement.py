import pdfplumber

from application.factory import create_app
from models.user import db, TransactionStatement1

# Create the Flask app instance
app = create_app()


def extract_table_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            # Extract tables from each page
            tables = page.extract_tables()

            for table in tables:
                # Check if it's the first page
                if page_index == 0:
                    # Skip the first two rows only on the first page
                    data_rows = table[2:]
                else:
                    # Process all rows on subsequent pages
                    data_rows = table

                # Iterate through rows and save to the database
                for row in data_rows:
                    no, date_time, comment, money, offset_name = row
                    print(date_time)
                    # save_transaction_to_db(date_time, comment, money, offset_name)


def extract_transaction_data(pdf_path):
    transactions = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            tables = page.extract_tables(table_settings={"vertical_strategy": "lines",
                                                         "horizontal_strategy": "text",
                                                         "snap_tolerance": 5})

            for table in tables:
                if page_index == 0:
                    data_rows = table[1:]
                else:
                    data_rows = table

                # Iterate through rows and save to the database
                for row in data_rows:  # Skip first two rows
                    # Extract relevant fields based on column order from your image
                    date_time_combined_doc_no = row[0].split("\n")
                    date_time = row[0]  # '01/09/2024'
                    doc_no = row[1]  # '5213.45946'
                    credit = row[2].split("\n")  # '50.000'
                    transaction_comment = row[5]  # '292976.010924.013647.xin cam on'

                    # Cleaning or converting data if necessary
                    credit = float(credit.replace('.', ''))

                    # Save the transaction as a dictionary (or insert it into a DB)
                    transaction1 = {
                        'date_time': date_time,
                        'doc_no': doc_no,
                        'credit': credit,
                        'transaction_comment': transaction_comment
                    }
                    print(transaction1)
                    transactions.append(transaction1)

    return transactions


def save_transaction_to_db(date_time, comment, money, offset_name):
    # Convert `money` to a float, if necessary
    money = float(money.replace('.', '').replace(',', '.'))

    # Create a new transaction record
    new_transaction = TransactionStatement1(
        date_time=date_time,
        transaction_comment=comment,
        credit=money,
        offset_name=offset_name
    )

    # Add the new transaction to the session and commit
    db.session.add(new_transaction)
    db.session.commit()


# Ensure that this block runs only if the script is executed directly
if __name__ == '__main__':
    # Establish the application context for the database operations
    with app.app_context():
        # Extract the table from the PDF and save to the database
        # extract_table_from_pdf("D:\\Working\\python\\VideoProcessor\\MTTQ.pdf")
        transaction_data = extract_transaction_data("D:\\Working\\python\\VideoProcessor\\MTTQ_VCB.pdf")
