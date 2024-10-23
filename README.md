
# DNSSEC Automation Project

This project automates DNSSEC (Domain Name System Security Extensions) configuration and management using a Flask web application and Paramiko for SSH connections to the DNS server.


## Set Up Python Environment

To set up the Python environment for this project:

1. Open the terminal in VS Code:

    Press Ctrl + \`` or navigate to Terminal > New Terminal`.

2. Create a virtual environment in the project directory:

    ```bash
    python3 -m venv .venv
    ```

3. Activate the virtual environment:

    3.1 On Windows:

    ```bash
    .venv\Scripts\activate
    ```

    3.2 On macOS and Linux:

    ```bash
    source .venv/bin/activate
    ```

4. After activation, you should see (.venv) in your terminal prompt, indicating that the virtual environment is active.


## Install Dependencies

Once the virtual environment is activated, install all the dependencies listed in the requirements.txt file.

```bash
pip install -r requirements.txt
```

This will install all required packages for the project.

## Configure VS Code

To ensure that VS Code uses the correct Python interpreter from your virtual environment:

1. Press Ctrl + Shift + P (or Cmd + Shift + P on macOS) to open the Command Palette.

2. Type and select Python: Select Interpreter.

3. Choose the interpreter from the .venv folder. It will be something like:

    ```bash
    ./.venv/bin/python
    ```

## Run the Flask Application

Once the virtual environment is activated and all dependencies are installed, you can run the Flask application.

Run via Terminal:

```bash
flask run
```

The app will be available at http://127.0.0.1:5000/.


## Contributing

If you wish to contribute to this project, feel free to submit a pull request. Please ensure that your code follows the project's coding standards and includes proper documentation.


