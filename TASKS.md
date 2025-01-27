# HOW TO SETUP:
1. Clone the repository to your local machine.
2. Activate your virtualenv
3. Install the required dependencies using `pip install -r requirements.txt`.
4. run `make upgrade sql run`
5. browse `http://127.0.0.1:5000/home/all/users`

# RUN TEST
> make test

# Workings
```bash
- removed redundant conversion to int for views
- tried not to install more libraries
- updated the existing ones I found since they're dated
- used Python 3.12
- extend/amend model classes as needed
- didn't use the factory method
- decided to use Makefile to do some little automation
- created a test config
- use black and isort to format .py files
- formatted html and js files
- reworked the migration as it had issues
- fixed a bug that used now() in model
- disabled future dates on new service additions
- utilized options instead of checkbox to reduce possibility of clash and errors.
- added form validation by making the required form fields required.
- added error handling for the endpoints.
```