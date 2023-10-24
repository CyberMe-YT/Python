import csv
import hashlib
import requests

def read_passwords_from_csv(csv_file):
    my_password_list = []

    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 2:  # Check if column 3 exists
                    password = row[2]
                    my_password_list.append(password)
    except FileNotFoundError:
        print(f"File {csv_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return my_password_list



def hash_passwords(password_list):
    hashed_passwords = []

    for password in password_list:
        # Convert the password to a SHA-1 hash
        sha1_hash = hashlib.sha1(password.encode()).hexdigest()
        hashed_passwords.append(sha1_hash)

    return hashed_passwords

def check_passwords_in_pwned_api(hashed_passwords):
    pwned_passwords = []

    for hashed_password in hashed_passwords:
        # Extract the first 5 characters of the hash to use in the API request
        prefix = hashed_password[:5]
        suffix = hashed_password[5:].upper()
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            response_lines = response.text.splitlines()
            for line in response_lines:
                line_prefix, count = line.split(':')
                if suffix == line_prefix:
                    print(f'Password hash {hashed_password} has been pwned {count} times.')
                    pwned_passwords.append(hashed_password)
                    break

    return pwned_passwords



# Example usage
csv_file = r'C:\temp\Yt-hibp\Database.csv'
password_list = read_passwords_from_csv(csv_file)
hashed_passwords = hash_passwords(password_list)
pwned_passwords = check_passwords_in_pwned_api(hashed_passwords)

