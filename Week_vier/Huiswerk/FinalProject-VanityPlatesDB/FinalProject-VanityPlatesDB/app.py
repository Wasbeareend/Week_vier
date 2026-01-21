from flask import Flask, render_template, request
import re
import string
from database import Database

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Create an instance of the Database class with the 'vanity.db' path
db = Database('vanity.db')

# Function to check if a sentence contains any punctuation
def checkPunctuation(sentence):
    for i in sentence:
        if i in string.punctuation:
            return False
    return True

# Function to check if a sentence contains a valid number
def checkNr(sentence):
    # Find all numbers in the sentence
    lijstNummers = re.findall(r'\d+', sentence)
    for i in lijstNummers:
        if i[0] == "0":
            return False
        if sentence.endswith(i) == False:
            return False
    return True

# Function to check if a given string is a valid license plate
def is_valid(s):
    if len(s) <= 6 and len(s) >= 2:
        # Check for specific conditions of a valid license plate
        if (
            checkPunctuation(s) == False
            or s[0].isalpha() == False
            or s[1].isalpha() == False
            or checkNr(s) == False
        ):
            return False
        return True
    else:
        return False


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # Retrieve the 'plate' value from the submitted form
        plate = request.form['plate']
        # Add the plate to the database
        db.add_numberPlates(plate)
        if is_valid(plate):
            # Render the 'valid.html' template with the valid plate
            return render_template('valid.html', plate=plate)
        else:
            # Render the 'invalid.html' template for an invalid plate
            return render_template('invalid.html')
    # Retrieve all number plates from the database
    plates = db.get_numberPlates()
    # Render the 'index.html' template with the list of plates
    return render_template('index.html', plates=plates)

if __name__ == "__main__":
    app.run(debug=True)
