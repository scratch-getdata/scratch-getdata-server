import pyotp
import time

# Replace 'GLB5IGYPJQVKV22GA432NRUHST2V2BG6' with your actual secret key
secret_key = 'GLB5IGYPJQVKV22GA432NRUHST2V2BG6'

# Load the initial counter value from a file or set it to 0 if the file doesn't exist
try:
    with open("otp_counter.txt", "r") as file:
        initial_counter = int(file.read())
except FileNotFoundError:
    initial_counter = 0

# Initialize the TOTP instance with the secret key
totp = pyotp.TOTP(secret_key)

# Set the initial counter value
totp.counter = initial_counter

while True:
    remaining_time = 30 - (int(time.time()) % 30)  # Calculate remaining time to the next 30-second interval
    print(f"Generated OTP: {totp.now()} (Next OTP in {remaining_time} seconds)")

    # Save the current counter value to the file
    with open("otp_counter.txt", "w") as file:
        file.write(str(totp.counter))

    time.sleep(remaining_time)
