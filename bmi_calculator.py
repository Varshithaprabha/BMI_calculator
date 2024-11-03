import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from matplotlib import pyplot as plt
from datetime import datetime

# Function to calculate BMI
def calculate_bmi(weight, height):
    try:
        height_m = height / 100  # convert cm to meters
        bmi = weight / (height_m ** 2)
        return round(bmi, 2)
    except ZeroDivisionError:
        return None

# Function to categorize BMI
def categorize_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"

# Database initialization
def init_db():
    conn = sqlite3.connect('bmi_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                weight REAL,
                height REAL,
                bmi REAL,
                category TEXT)''')
    conn.commit()
    conn.close()

# Function to save BMI data
def save_bmi_data(weight, height, bmi, category):
    conn = sqlite3.connect('bmi_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO bmi_records (date, weight, height, bmi, category) VALUES (?, ?, ?, ?, ?)",
              (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), weight, height, bmi, category))
    conn.commit()
    conn.close()

# Function to retrieve BMI data
def get_bmi_data():
    conn = sqlite3.connect('bmi_data.db')
    c = conn.cursor()
    c.execute("SELECT date, bmi FROM bmi_records ORDER BY date ASC")
    data = c.fetchall()
    conn.close()
    return data

# Function to plot BMI data
def plot_bmi_data():
    data = get_bmi_data()
    if len(data) == 0:
        QMessageBox.information(None, "No Data", "No BMI data available to visualize.")
        return
    
    dates, bmi_values = zip(*data)
    
    plt.figure(figsize=(10, 5))
    plt.plot(dates, bmi_values, marker='o', linestyle='-', color='b')
    plt.xlabel('Date')
    plt.ylabel('BMI')
    plt.title('BMI Trend Over Time')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# PyQt5 GUI class
class BMICalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('BMI Calculator')

        # Layout
        layout = QVBoxLayout()

        # Weight input
        self.weight_label = QLabel('Weight (kg):')
        layout.addWidget(self.weight_label)
        self.weight_input = QLineEdit()
        layout.addWidget(self.weight_input)

        # Height input
        self.height_label = QLabel('Height (cm):')
        layout.addWidget(self.height_label)
        self.height_input = QLineEdit()
        layout.addWidget(self.height_input)

        # BMI result
        self.bmi_label = QLabel('BMI: ')
        layout.addWidget(self.bmi_label)

        # Category result
        self.category_label = QLabel('Category: ')
        layout.addWidget(self.category_label)

        # Calculate button
        self.calculate_button = QPushButton('Calculate BMI')
        self.calculate_button.clicked.connect(self.on_calculate_bmi)
        layout.addWidget(self.calculate_button)

        # Plot button
        self.plot_button = QPushButton('Show BMI Trends')
        self.plot_button.clicked.connect(plot_bmi_data)
        layout.addWidget(self.plot_button)

        # Set the layout
        self.setLayout(layout)

    # BMI Calculation with validation
    def on_calculate_bmi(self):
        try:
            weight = float(self.weight_input.text())
            height = float(self.height_input.text())

            if weight <= 0 or height <= 0:
                raise ValueError("Weight and height must be positive numbers.")

            bmi = calculate_bmi(weight, height)
            if bmi is None:
                raise ValueError("Invalid BMI calculation.")

            category = categorize_bmi(bmi)

            self.bmi_label.setText(f"BMI: {bmi}")
            self.category_label.setText(f"Category: {category}")

            # Save data to the database
            save_bmi_data(weight, height, bmi, category)

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))

# Main function
if __name__ == '__main__':
    # Initialize the database
    init_db()

    # Run the application
    app = QApplication(sys.argv)
    window = BMICalculator()
    window.show()
    sys.exit(app.exec_())
