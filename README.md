![logo](https://github.com/sajji18/TinkerQuest-24/blob/main/media/logo.jpeg)

<div align="center">

</div>

# ⛑️ DocAI

<br>

## 💻 About DocAI

### Features
DocAI streamlines the report-making process by automating key tasks while ensuring the authenticity of medical information. Here's how our application addresses these challenges:

1. **Automated Report Generation**: DocAI leverages machine learning and natural language processing (NLP) techniques to automate report creation. Doctors can focus on patient care while our system generates accurate and concise reports.

2. **User-Friendly Interface**: Our intuitive web interface, built using Django and Ajax, provides a seamless experience for both doctors and patients. Users can easily input data, view reports, and access relevant information.

3. **Enhanced Readability**: We use Plotly and Plotly Express to create interactive visualizations within reports. Graphs, charts, and diagrams help convey complex medical data in a clear and digestible format.

4. **Secure Authentication**: Google OAuth3 integration ensures secure access for authorized users. Doctors can log in securely and manage patient data.

5. **Virtual Assistant Bot**: DocAI introduces an NLP-powered chatbot that educates users about minor symptoms, preventive measures, and general health awareness. This innovative feature enhances patient engagement and promotes well-being.


## 📫 Run Locally

To use DocAI, follow these steps:
1. Clone this repository.
```bash
  git clone https://github.com/sajji18/TinkerQuest-24.git
```
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up your Google OAuth credentials.
4. To create an admin user run `python manage.py createsuperuser`.
5. To create a doctor account run `python manage.py create_user`.
6. Run the Django development server: `python manage.py runserver`.
7. Access the application at
`http://localhost:8000`.

## 📖 Video Demonstration and Presentation

- [Presentation](https://docs.google.com/presentation/d/17KsKaxRCzVPJdcxRNS669vafY8-4H6o8kgXtJ7Dvdbg/edit?usp=sharing)
- [Video Presentation](https://drive.google.com/drive/folders/1tt6ddJLIdU-V4CypO0hqysUdEBw2kHub?usp=drive_link)


## 🛠️ Tech Stack

**Client/FrontEnd:**

- Django: Our web application framework of choice for building the frontend.

- Ajax: Used for asynchronous communication between the client and server, enhancing the user experience.

- Sqllite3: The lightweight database engine, suitable for development and testing purposes.

- Google OAuth3: For secure authentication and authorization of users.


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
| Report Generation and export | Planned     | Didnt apply              |



## 📃 Future Strategic Objectives

- Database and Chart Compatibility: Designing the database beforehand can often be found a good practice and we found it the hard way.
- Chart Integration: Dash was the first time we used , hence the integration of the Chart utility could have been better if we had known its use better
- Route Protection: We could have used React to enhance the UI but integration seemed a bit tiresome since we wanted to use django
- Dark Mode theme: An Additional utility like this could be easily added using React
- NLP Optimization: could be easier with the use of newer methods or by using llama 7b however , we wanted to work it out from scratch
- Bearable Value Visualisation: Customisable Values to have a better showcase of limited or range of values that are normal for health could be added , customising this would be easier in react
- Report generation : Due to loss of time , pdf was not generated from the HTML , this can be added later



## ✨ Contributors-
- [Siddhant Gupta](https://github.com/SidWorks01) , PnI 2nd year
 - [Sajal Chauhan](https://github.com/sajji18) , PnI 2nd year
