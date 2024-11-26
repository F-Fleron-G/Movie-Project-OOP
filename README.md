# Movie App 📽️

A simple and interactive Movie Management application that lets users add, update, delete, and search for movies. The app integrates with the OMDb API to fetch movie details and even generates a website showcasing your movie collection!

---

## Features ☆
- **Add Movies**: Fetch movie details from the OMDb API and add them to your collection.
- **Update Movies**: Add personalized notes to your movies.
- **Delete Movies**: Remove movies you no longer need.
- **Search Movies**: Quickly find movies by title.
- **Generate Website**: Automatically create a visually appealing HTML page to display your movie collection.

---

## Setup and Installation ⚙️

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd <project-folder>
   
2. Set up dependencies: Make sure you have Python installed, then install the required modules:
    ```bash
    pip install -r requirements.txt

3. Set up the environment: Create a .env file in the project root and add your OMDb API key:
   Head over to https://www.omdbapi.com/ for your API key.
   ```bash
   API_KEY=your_api_key_here
   
4. Run the application: Launch the program by running the following command:
   ```bash
   python main.py

---

## Project Structure 📂

├── data/
│   └── movies.json        
├── static/                
├── storage/               
├── main.py                
├── movie_app.py           
├── requirements.txt       
├── README.md              
└── .gitignore      

---

## Dependencies 🛠️

The project uses the following Python libraries:

- **requests**: To fetch movie data from the OMDb API.
- **python-dotenv**: To manage the OMDb API key securely.

To install dependencies, run: pip install - requirements.txt

---
## Contributing 🤝

Contributions are welcome! If you’d like to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name

3. Commit your changes and push them to your branch.
4. Submit a pull request.

