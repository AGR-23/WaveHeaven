# WaveHeaven - Automatic Volume Adjustment Web Application
WaveHeaven is a web application developed with Django that provides an intelligent automatic volume adjustment system. It dynamically adapts audio settings based on ambient noise and user preferences, offering a personalized listening experience.
****

# Table of Contents

[Prerequisites](https://github.com/AGR-23/WaveHeaven?tab=readme-ov-file#prerequisites)

[Installation](https://github.com/AGR-23/WaveHeaven?tab=readme-ov-file#installation)

[Running the Application](https://github.com/AGR-23/WaveHeaven?tab=readme-ov-file#running-the-application)

[Installing the Chrome Extension](https://github.com/AGR-23/WaveHeaven?tab=readme-ov-file#installing-the-chrome-extension)

[How to Use the Extension](https://github.com/AGR-23/WaveHeaven?tab=readme-ov-file#how-to-use-the-extension)
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
- **Install requirements:**
Since this project is built with Django, you need to install Django, and other things if it's not already installed. Run the following command:

```
pip install -r requirements.txt
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

**Deactivating the Virtual Environment**
Once you're done using WaveHeaven, it's good practice to deactivate your virtual environment. Simply run:
```
deactivate
```

# Installing the Chrome Extension
This extension works only on Google Chrome. Follow these steps to install it:

- Open Chrome and click the three-dot menu in the top right corner.

- Go to **"Extensions"** → "Manage Extensions".

- Enable Developer Mode in the top right corner of the Extensions page.

- Click on "Load unpacked" in the top left corner.

- Navigate to the following folder inside the cloned repository:
  
```
WaveHeaven/waveheavenproject/weaveheaven-extension
```

- Select that folder and the extension will be added to Chrome.

**Optional: Right-click the WaveHeaven icon and select "Pin" to keep it easily accessible.**

# How to Use the Extension

Make sure the WaveHeaven dashboard is open in a browser tab. You need this open to select your first sound profile.

Once the first sound profile is selected, you can switch between profiles from anywhere — that's the magic of the extension!

When a profile is applied, a timer will start tracking your listening time. You can pause or reset the timer as needed.

**🔔 NOTE: Currently, the sound profile selection does not change the equalizer due to time constraints and complexity (this is our first browser extension). However, the extension can adjust the overall tab volume, delivering a working MVP. Future improvements are on the way!**

