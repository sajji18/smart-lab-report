#!bin/bash

venv_setup () {
    ### 
        # Function Description:
            # Create a virtual Environment
            # Activate this created environment
            # Install required packaged remotely in the environment
    ###
    echo "Setting up the Virtual Environment....."

    python -m venv .env
    source .env/Scripts/activate
    pip install -r requirements.txt

    echo "Virtual Enviroment Setup is Complete"
}

django_setup () {
    ### 
        # Function Description:
            # Create the scripts for the initial database with default django classes
            # Execute the scripts to create the database
    ###
    echo "Database setup starting....."

    python manage.py makemigrations
    python manage.py migrate

    echo "Database setup Complete"
}

create_super_user () {
    ### 
        # Function Description:
            # Take input of username, email and password
            # Run the custom script to create the super user
    ###
    echo "Creating an Admin Account....."

    read -p "Enter Username: " username
    read -p "Enter Email: " email
    read -p "Enter Password: " password

    python manage.py auto_createsuperuser --username $username --email $email --password $password

    echo "Admin Account Creation Finished"
}

create_doctor_user () {
    ### 
        # Function Description:
            # Take input of username, email, password and user_type
            # Run the custom script to create the doctor account (Only way to create a doctor account)
    ###
    echo "Creating a Doctor Account....."

    read -p "Enter Username: " username
    read -p "Enter Email: " email
    read -p "Enter Password: " password
    read -p "Enter doctor as user type: " usertype

    python manage.py create_user --username $username --email $email --password $password --user_type $usertype

    echo "Setup Ended... :D"
}

venv_setup
django_setup
create_super_user
create_doctor_user