# WaveHeaven - Automatic Volume Adjustment Web Application
WaveHeaven is a web application developed with Django that provides an intelligent automatic volume adjustment system. It dynamically adapts audio settings based on ambient noise and user preferences, offering a personalized listening experience.
****

# Table of Contents

[Prerequisites]()

[Installation]()

[Running the Application]()

****

## Prerequisites
Before you begin, ensure you have the following installed:

- **Python 3.8 or higher:** The application is built using Python and Django. You can download Python from python.org.

- **Git:** To clone the repository. You can download Git from git-scm.com.
****

## Installation
Follow these steps to set up the project on your local machine:

- **Clone the repository:**
Open your terminal and run the following command to clone the repository:
```
git clone https://github.com/AGR-23/WaveHeaven.git
```

- **Navigate to the project directory:**
After cloning the repository, navigate to the project folder:

```
cd WaveHeaven/waveheavenproject
```

- **Set up a virtual environment (optional but recommended):**
It's a good practice to use a virtual environment to manage dependencies. You can create one using the following commands:

# For Windows
```
python -m venv venv
venv\Scripts\activate
```

# For Linux/MacOS
```
python3 -m venv venv
source venv/bin/activate
```
- **Install Django:**
Since this project is built with Django, you need to install Django if it's not already installed. Run the following command:

```
pip install django
```
****

# Running the Application
Once the setup is complete, you can run the application locally by following these steps:

- **Start the Django development server:**
Run the following command to start the Django development server:

# For Windows
```
py manage.py runserver
```

# For Linux/MacOS
```
python3 manage.py runserver
```

- **Access the application:**
Open your favorite web browser and navigate to the following URL:

```
http://127.0.0.1:8000/
```
**You should now see the WaveHeaven homepage.**
