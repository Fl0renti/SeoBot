from email_validator import validate_email, EmailNotValidError


email = "sssd@gmail.com"
# email = "fatlindthaci@gmail.com"

try:
    # Check that the email address is valid.
    emailinfo = validate_email(email, check_deliverability=True)

    # After this point, use only the normalized form of the email address,
    # especially before going to a database query.
    email = emailinfo.normalized

    # Print success message
    print("The email address is valid and normalized:")

except EmailNotValidError as e:
    print(e)