import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QDateEdit, QMessageBox)
from PyQt5.QtCore import Qt, QDate

class PaymentTrackerApp(QWidget):
    CSV_FILE = 'payment_records.csv'

    def __init__(self):
        super().__init__()
        self.load_or_create_csv()
        self.initUI()

    def load_or_create_csv(self):
        try:
            df = pd.read_csv(self.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Date', 'First Name', 'Last Name', 'Service Type', 'Payment'])
            df.to_csv(self.CSV_FILE, index=False)

    def initUI(self):
        self.setWindowTitle('Payment Tracker')
        self.setGeometry(100, 100, 600, 650)

        main_layout = QVBoxLayout()

        # Input Section
        input_layout = QVBoxLayout()

        # Date Input
        date_layout = QHBoxLayout()
        date_label = QLabel('Date:')
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        input_layout.addLayout(date_layout)

        # First Name Input
        first_name_layout = QHBoxLayout()
        first_name_label = QLabel('First Name:')
        self.first_name_input = QLineEdit()
        first_name_layout.addWidget(first_name_label)
        first_name_layout.addWidget(self.first_name_input)
        input_layout.addLayout(first_name_layout)

        # Last Name Input
        last_name_layout = QHBoxLayout()
        last_name_label = QLabel('Last Name:')
        self.last_name_input = QLineEdit()
        last_name_layout.addWidget(last_name_label)
        last_name_layout.addWidget(self.last_name_input)
        input_layout.addLayout(last_name_layout)

        # Service Type Dropdown
        service_layout = QHBoxLayout()
        service_label = QLabel('Service Type:')
        self.service_dropdown = QComboBox()
        self.service_dropdown.addItems(['Home Inspection', 'Mold', 'Radon', 'Water', 'Sewer Scope', 'Other'])
        service_layout.addWidget(service_label)
        service_layout.addWidget(self.service_dropdown)
        input_layout.addLayout(service_layout)

        # Payment Input
        payment_layout = QHBoxLayout()
        payment_label = QLabel('Payment Amount:')
        self.payment_input = QLineEdit()
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.payment_input)
        input_layout.addLayout(payment_layout)

        # Submit and Update Buttons
        button_layout = QHBoxLayout()
        self.submit_button = QPushButton('Submit Payment Record')
        self.submit_button.clicked.connect(self.submit_record)
        self.update_button = QPushButton('Update Selected Record')
        self.update_button.clicked.connect(self.update_record)
        self.update_button.setEnabled(False)
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.update_button)
        input_layout.addLayout(button_layout)

        # Filters Section
        filter_layout = QVBoxLayout()
        filter_label = QLabel('Filter Records:')
        filter_layout.addWidget(filter_label)

        # Month Filter
        month_layout = QHBoxLayout()
        month_label = QLabel('Month:')
        self.month_filter = QComboBox()
        self.month_filter.addItems(['All'] + [f'{i:02d}' for i in range(1, 13)])
        month_layout.addWidget(month_label)
        month_layout.addWidget(self.month_filter)
        filter_layout.addLayout(month_layout)

        # Year Filter
        year_layout = QHBoxLayout()
        year_label = QLabel('Year:')
        self.year_filter = QComboBox()
        self.year_filter.addItems(['All', '2024', '2025'])
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_filter)
        filter_layout.addLayout(year_layout)

        # Apply Filter Button
        self.filter_button = QPushButton('Apply Filter')
        self.filter_button.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.filter_button)

        # Record Selection for Editing
        select_record_layout = QVBoxLayout()
        select_record_label = QLabel('Select Record to Edit:')
        self.record_selector = QComboBox()
        self.record_selector.addItem('None')
        self.record_selector.currentIndexChanged.connect(self.load_selected_record)
        select_record_layout.addWidget(select_record_label)
        select_record_layout.addWidget(self.record_selector)
        filter_layout.addLayout(select_record_layout)

        # Output Section
        output_label = QLabel('Payment Records:')
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        # Add all sections to the main layout
        main_layout.addLayout(input_layout)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(output_label)
        main_layout.addWidget(self.output_text)

        self.setLayout(main_layout)
        self.load_records()

    def submit_record(self):
        if self.validate_inputs():
            date = self.date_input.date().toString("yyyy-MM-dd")
            first_name = self.first_name_input.text()
            last_name = self.last_name_input.text()
            service_type = self.service_dropdown.currentText()
            payment = self.payment_input.text()

            try:
                df = pd.read_csv(self.CSV_FILE)
                new_record = pd.DataFrame({
                    'Date': [date],
                    'First Name': [first_name],
                    'Last Name': [last_name],
                    'Service Type': [service_type],
                    'Payment': [payment]
                })
                df = pd.concat([df, new_record], ignore_index=True)
                df.to_csv(self.CSV_FILE, index=False)
                self.load_records()
                self.clear_inputs()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save record: {str(e)}")

    def validate_inputs(self):
        if not self.first_name_input.text():
            QMessageBox.warning(self, "Input Error", "Please enter first name")
            return False
        if not self.last_name_input.text():
            QMessageBox.warning(self, "Input Error", "Please enter last name")
            return False
        try:
            float(self.payment_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid payment amount")
            return False
        return True

    def load_records(self):
        try:
            df = pd.read_csv(self.CSV_FILE)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Apply filters
            month = self.month_filter.currentText()
            year = self.year_filter.currentText()
            filtered_df = df.copy()
            if month != 'All':
                filtered_df = filtered_df[filtered_df['Date'].dt.month == int(month)]
            if year != 'All':
                filtered_df = filtered_df[filtered_df['Date'].dt.year == int(year)]
            filtered_df = filtered_df.sort_values('Date', ascending=False)

            # Update record selector
            self.record_selector.clear()
            self.record_selector.addItem('None')
            for idx, row in filtered_df.iterrows():
                self.record_selector.addItem(
                    f"{idx}: {row['Date'].strftime('%Y-%m-%d')} - {row['First Name']} {row['Last Name']}"
                )

            self.display_records(filtered_df)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading records: {str(e)}")
            self.output_text.setPlainText(f"Error loading records: {e}")

    def display_records(self, df):
        if df.empty:
            self.output_text.setPlainText("No records found.")
            return

        df['Payment'] = df['Payment'].astype(float)
        max_widths = {col: max(df[col].astype(str).str.len().max(), len(col)) for col in df.columns}
        header = "Date  First Name  Last Name  Service Type  Payment"
        underline = '-' * len(header)
        rows = [
            f"{row['Date'].strftime('%Y-%m-%d')}  {row['First Name']}  {row['Last Name']}  {row['Service Type']}  {row['Payment']:.2f}"
            for _, row in df.iterrows()
        ]
        total_payment = df['Payment'].sum()
        total_row = f"Total Payment: {total_payment:.2f}"
        output = "\n".join([header, underline] + rows + [underline, total_row])
        self.output_text.setPlainText(output)

    def load_selected_record(self):
        selected = self.record_selector.currentText()
        if selected == 'None' or selected == '':
            self.clear_inputs()
            self.update_button.setEnabled(False)
            return

        try:
            idx = int(selected.split(':')[0])
            df = pd.read_csv(self.CSV_FILE)
            record = df.loc[idx]
            self.date_input.setDate(QDate.fromString(record['Date'], "yyyy-MM-dd"))
            self.first_name_input.setText(record['First Name'])
            self.last_name_input.setText(record['Last Name'])
            self.service_dropdown.setCurrentText(record['Service Type'])
            self.payment_input.setText(str(record['Payment']))
            self.update_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading record {str(e)}")

    def update_record(self):
        selected = self.record_selector.currentText()
        if selected == 'None':
            return

        try:
            idx = int(selected.split(':')[0])
            if not self.validate_inputs():
                return

            df = pd.read_csv(self.CSV_FILE)
            df.loc[idx, 'Date'] = self.date_input.date().toString("yyyy-MM-dd")
            df.loc[idx, 'First Name'] = self.first_name_input.text()
            df.loc[idx, 'Last Name'] = self.last_name_input.text()
            df.loc[idx, 'Service Type'] = self.service_dropdown.currentText()
            df.loc[idx, 'Payment'] = self.payment_input.text()
            df.to_csv(self.CSV_FILE, index=False)
            self.load_records()
            QMessageBox.information(self, "Success", "Record updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating record: {str(e)}")

    def apply_filters(self):
        self.load_records()

    def clear_inputs(self):
        self.date_input.setDate(QDate.currentDate())
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.service_dropdown.setCurrentIndex(0)
        self.payment_input.clear()
        self.update_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    payment_app = PaymentTrackerApp()
    payment_app.show()
    sys.exit(app.exec_())