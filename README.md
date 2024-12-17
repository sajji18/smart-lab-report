![logo](https://github.com/sajji18/TinkerQuest-24/blob/main/media/logo.jpeg)

<div align="center">

</div>

# ⛑️ DocAI

<br>

## 💻 About DocAI

### Features
DocAI streamlines the report-making process by automating key tasks while ensuring the authenticity of medical information. Here's how our application addresses these challenges:

1. **Automated Report Generation**: DocAI leverages natural language processing (NLP) techniques to automate report creation. Doctors can focus on patient care while our system generates accurate and concise reports.

2. **User-Friendly Interface**: Our intuitive web interface, built using Django and Ajax, provides a seamless experience for both doctors and patients. Users can easily input data, view reports, and access relevant information.

3. **Enhanced Readability**: We use Plotly and Plotly Express to create interactive visualizations within reports. Graphs, charts, and diagrams help convey complex medical data in a clear and digestible format.

4. **Secure Authentication**: Google OAuth3 integration ensures secure access for authorized users. Doctors can log in securely and manage patient data.

5. **Virtual Assistant Bot**: DocAI introduces an NLP-powered chatbot that educates users about minor symptoms, preventive measures, and general health awareness. This innovative feature enhances patient engagement and promotes well-being.


## 📫 Run Locally

To use DocAI, follow these steps:
1. Clone this repository.
```bash
  git clone https://github.com/sajji18/smart-lab-report.git
```
2. Setup virtual enviroment with: `python -m venv <env_name>` and activate it using `source <env_name>/Scripts/activate` on bash. Now, Install the required dependencies using `pip install -r requirements.txt`.
3. Set up your Google OAuth credentials from the Google API Console and download the required secrets.json. Create your own `secrets.json` in the base directory and exactly follow the .example.secret.json for format.
4. Create an admin superuser account from terminal with `python manage.py createsuperuser`.
5. Go to `http://localhost:8000/admin`, and log in using the superuser credentials.
6. From the sites option in the left sidebar, create a new site with:  `domain name: localhost:8000` and `display name: localhost`.
7. Now from social applications option in the left sidebar, create a new application: Set `Provider: Google`, `name` as you wish, YOUR `client_id`, `client_secret` and add the previously create site from `available sites` to `chosen sites`.
8. Create a doctor account from terminal with `python manage.py create_user`.
9. Now from Test option in the left sidebar, create a new test: (Either Blood Test or Diabetes Test) using the previously created doctor account of your choice.
10. Run the Django development server from the terminal: `python manage.py runserver`.
11. Access the application at: `http://localhost:8000`.
12. Create and log into a new customer account.
13. Now again in the admin dashboard, `http://localhost:8000/admin`, create a Test Application from left sidebar (Means User Applied for a Test), for the previously created customer account with the tests created by the doctor.
14. Now you can operate from the web app only.

## 📖 Video Demonstration and Presentation

- [Presentation](https://docs.google.com/presentation/d/1nrtJG3l_0ww4Z69G-tgB3c0DvNjrUWXLFO4da1JiTXo/edit?usp=sharing)
- [Video Presentation](https://drive.google.com/drive/folders/1tt6ddJLIdU-V4CypO0hqysUdEBw2kHub?usp=drive_link)


## 🛠️ Tech Stack

**Client/FrontEnd:**

- Django: Our web application framework of choice for building the backend.

- Ajax: Used for asynchronous communication between the client and server, enhancing the user experience.

- Sqlite3: The lightweight database engine, suitable for development and testing purposes.

- Google OAuth2: For secure authentication and authorization of users.


**ML/Data:**

- Dash: Utilized for creating interactive, web-based data visualizations to enhance report readability.

- Django all-auth: Provides authentication and authorization features, ensuring secure access to the application.

- Plotly: A powerful visualization library used for creating dynamic and engaging charts within the reports.

- Plotly Express: Simplifies the creation of complex visualizations, further enhancing the report's clarity.

- torch: PyTorch is employed for machine learning tasks, aiding in the automation of report generation.

- nltk: Natural Language Toolkit used for processing natural language, facilitating the integration of text-based features like the chatbot.


## 🛠️ Challenges Faced

## Problem and Approach


| Problems  | Approach | Status                   | 
| :-------- | :------- | :------------------------- |
| Database Design| Hit and Trial | Decent |
| Ajax Dynamic Updates | Planned    | Good               |
| Chatbot Integration | Research     | Good               |
| Chart Integration | Research     | Decent              |
| Database and Chart Compatibility | Hit and Trial     | Poor                |
| Route Protection | Planned     |    Decent      |
| Chat Utility | Planned     | Good              |
| Dark Mode Theme | Unplanned     | Could be Better               |
| NLP/bot optimization | Research     | Could be Better               |
| Bearable Value Visualisation | Unplanned     | Didnt Apply             |
| Report Generation and export | Planned     | Decent             |



## 📃 Future Strategic Objectives

- Database and Chart Compatibility: Designing the database beforehand can often be found a good practice and we found it the hard way.
- Chart Integration: Dash was the first time we used , hence the integration of the Chart utility could have been better if we had known its use better
- Visual Appeal: We could have used React to enhance the UI but integration seemed a bit tiresome since we wanted to use django
- Dark Mode theme: An Additional utility like this could be easily added using React
- NLP Optimization: could be easier with the use of newer methods or by using llama 7b however , we wanted to work it out from scratch
- Bearable Value Visualisation: Customisable Values to have a better showcase of limited or range of values that are normal for health could be added , customising this would be easier in react



## ✨ Contributors-
- [Siddhant Gupta](https://github.com/SidWorks01)
- [Sajal Chauhan](https://github.com/sajji18)
