import requests
from dotenv import load_dotenv
import os

load_dotenv()

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
PURPLE = "\033[95m"
RESET = "\033[0m"


def normalize_movie_name(movie_name):
    """
        Cleans up a movie name for consistent usage.

        Strips unnecessary spaces and converts the name to lowercase for easier
        comparisons and searches.

        Args:
            movie_name (str): The movie title to normalize.

        Returns:
            str: A cleaned, lowercase version of the movie name.
        """
    return movie_name.strip().lower()


def capitalize_movie_name(movie_name):
    """
    Formats a movie name to be more presentable.

    Strips unnecessary spaces and capitalizes each word in the movie name.

    Args:
        movie_name (str): The movie title to format.

    Returns:
        str: A nicely capitalized version of the movie name.
    """
    return movie_name.strip().title()


class MovieApp:
    def __init__(self, storage):
        """
        Sets up the MovieApp with a storage system.

        This method connects the app to a storage system that handles the
        database of movies. The storage system must implement methods like
        adding, deleting, and updating movie details.

        Args:
            storage: An object that implements the IStorage interface.
        """
        self._storage = storage
        self.api_url = "http://www.omdbapi.com/"
        self.api_key = os.getenv("API_KEY")

    def add_movie(self):
        """
        Adds a new movie to the collection by fetching details from OMDb.

        This method allows to search for a movie using its title. It fetches
        data like the release year, IMDb rating, and poster from the OMDb API
        and saves it to the collection.

        Steps:
        1. Enter the movie's title when prompted.
        2. The app fetches details from OMDb and stores them in your collection.

        Notes:
            - If the movie isn't found in OMDb, it provides a friendly message.
            - Ensure the `.env` file contains a valid API key for OMDb.

        Example:
            Add a movie titled "Inception," and it will fetch the details and save
            them to view later.
        """
        movie_title = input(f"{GREEN}Please enter a movie title:{RESET} ").strip()

        normalized_title = normalize_movie_name(movie_title)

        params = {"apikey": self.api_key, "t": normalized_title}
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()

            movie_data = response.json()

            if movie_data.get("Response") == "False":
                print(f"Movie {YELLOW}'{movie_title}'{RESET} not found in OMDb database.")
                return

            title = movie_data.get("Title", "Unknown")
            year = int(movie_data.get("Year", 0))
            rating = float(movie_data.get("imdbRating", 0.0))
            poster_url = movie_data.get("Poster", "N/A")
            imdbID = movie_data.get("imdbID", "N/A")

            self._storage.add_movie(
                normalized_title, {
                    "rating": rating,
                    "year": year,
                    "poster": poster_url,
                    "imdbID": imdbID
                }
            )

            print(f"{PURPLE}Movie '{capitalize_movie_name(title)}' added"
                  f" successfully!{RESET}\n")

        except requests.exceptions.RequestException as e:
            print(f"{RED}An error occurred while accessing the OMDb API. Please try again"
                  f" later.{RESET}")
            print(f"{RED}Error details: {e}{RESET}")

    def _command_list_movies(self):
        """
        Lists all the movies in the collection.

        Displays movies stored in the database with their titles, release year,
        and IMDb rating.
        """
        movies = self._storage.list_movies()
        if movies:
            movie_list_title = "Current Listed Movies:"
            print(f"\n{movie_list_title}\n{YELLOW}{'‾' * len(movie_list_title)}{RESET}")
            for title, details in movies.items():
                year = details.get("year", "Unknown Year")
                rating = details.get("rating", "N/A")
                print(f"{YELLOW}{capitalize_movie_name(title)}{RESET} | "
                      f"{CYAN}{year}{RESET} | "
                      f"Rating: {CYAN}{rating}{RESET}")
            print()
        else:
            print(f"{RED}Oops! No movies found in the database.{RESET}")

    def delete_movie(self):
        """
        Removes a movie from the collection.

        Allows the user to delete a movie by its title. If the movie isn't found in
        the database, a friendly message will appear.

        Steps:
        1. Enter the movie's title when prompted.
        2. The app checks if the movie exists and deletes it.

        Example:
            Delete a movie titled "Titanic" from the collection.

        Notes:
            - Make sure to enter the exact title you used when adding the movie.
        """
        try:
            movie_title = input(f"{GREEN}Please enter the movie to delete:{RESET} ").strip()

            normalized_title = normalize_movie_name(movie_title)

            movies = self._storage.list_movies()

            if normalized_title in movies:
                self._storage.delete_movie(normalized_title)
                print(f"{YELLOW}'{capitalize_movie_name(movie_title)}'{RESET} has "
                      f"been successfully deleted.\n")
            else:
                print(
                    f"{RED}Movie{RESET} {YELLOW}'{capitalize_movie_name(movie_title)}'"
                    f"{RESET}{RED} not found in the list.{RESET}")

        except Exception as e:
            print(f"{RED}An error occurred: {e}{RESET}")

    def update_movie(self):
        """
        Updates the details of an existing movie in the collection.

        This allows to add or update a note for a movie that's already in the
        collection. Simply enter the movie's title, and if it exists in the
        database, you can provide new notes for it. If the movie isn't found, a
        friendly message will appear.

        Steps:
        1. Enter the name of the movie you'd like to update.
        2. If the movie exists, new notes can be added (up to 100 characters).
        3. The notes will be saved and can be viewed later.

        Notes:
            - Make sure to enter the exact movie title you used when adding it.
            - The system will normalize titles to handle small inconsistencies like
              extra spaces or different capitalization.
        """
        movies = self._storage.list_movies()
        movie_name = input(f"{GREEN}Please enter the movie name:{RESET} ").strip()
        normalized_name = normalize_movie_name(movie_name)

        if normalized_name not in movies:
            print(f"Movie {YELLOW}'{movie_name}'{RESET} not found!")
            return

        notes = input(f"{GREEN}Please enter your notes for the movie:{RESET} ").strip()
        notes = notes[:100]

        movie_details = movies[normalized_name]
        movie_details["notes"] = notes

        try:
            self._storage.update_movie(normalized_name, movie_details)
            print(f"Notes for {YELLOW}'{capitalize_movie_name(movie_name)}'"
                  f"{RESET} successfully updated!\n")
        except ValueError as e:
            print(f"{RED}Error updating movie: {e}{RESET}")

    def search_movie(self):
        """
        Searches the collection for movies that match a keyword.

        This method allows to search for movies by their title or part of
        their title. Matching movies will be displayed with their details.

        Steps:
        1. Enter a keyword to search for.
        2. View all matching movies, including their title, rating, year, and IMDb link.

        Notes:
            - The search is case-insensitive and can match partial titles.
            - If no matches are found, a friendly message will appear.
        """
        search_query = input(f"{GREEN}Please enter the movie title to search:"
                             f"{RESET} ").strip()

        normalized_query = normalize_movie_name(search_query)

        movies = self._storage.list_movies()

        found_movies = []

        for title, details in movies.items():
            normalized_title = normalize_movie_name(title)

            if normalized_query in normalized_title:
                found_movies.append((title, details))

        if found_movies:
            print(f"\nFound movies matching {YELLOW}'"
                  f"{capitalize_movie_name(search_query)}'"
                  f":{RESET}\n")
            for title, details in found_movies:
                imdb_link = f"https://www.imdb.com/title/{details['imdbID']}"
                print(f"{YELLOW}{capitalize_movie_name(title)}{RESET} - "
                      f"Rating: {CYAN}{details['rating']}{RESET} | Year:"
                      f" {CYAN}{details['year']}{RESET}")
                print(f"IMDb Link: {imdb_link}\n")
        else:
            print(f"{RED}No movies found matching '"
                  f"{capitalize_movie_name(search_query)}'.{RESET}")

    def generate_website(self):
        """
        Creates an HTML webpage for the movie collection.

        This function transforms the movie database into an organized
        webpage with all the movies that have been added. Each movie will
        include details like its title, year, IMDb rating, poster, and the
        notes/comments (if available).

        Steps:
        1. Reads an HTML template stored in `static/index_template.html`.
        2. Populates the template with movie details from the collection.
        3. Generates a new file named `index.html` that can be opened in the browser.

        Notes:
            - Add more movies to increase the collection on the webpage!
            - Users can share their generated `index.html` with friends to show off
              their favorite picks.

        Error Handling:
            - If the template file is missing or there's an unexpected error,
              a friendly error message will appear.
        """
        try:
            with open('static/index_template.html', 'r') as template_file:
                template = template_file.read()

            template = template.replace('__TEMPLATE_TITLE__',
                                        'My Movie App')

            movies = self._storage.list_movies()
            movie_grid = ""

            for title, details in movies.items():
                omdb_link = f"https://www.imdb.com/title/{details['imdbID']}"
                notes = details.get('notes', 'No notes available')
                movie_grid += f"""
                    <li id="movie-{details['imdbID']}">
                        <a href="{omdb_link}" target="_blank">
                            <img src="{details['poster']}" alt="Poster of {title}"
                             class="movie-poster" title="{notes}" />
                        </a>
                        <b>{capitalize_movie_name(title)}</b><br>Rating: {details['rating']} ✩
                         | Year: {details['year']}
                    </li>
                """

            template = template.replace('__TEMPLATE_MOVIE_GRID__', movie_grid)

            with open('index.html', 'w') as output_file:
                output_file.write(template)

            print(f"{CYAN}Website was generated successfully!{RESET}\n")

        except FileNotFoundError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"{RED}An unexpected error occurred: {e}{RESET}")

    def run(self):
        """
        Runs the MovieApp, showing a menu to interact with the collection.

        This method displays an interactive menu where one can perform actions
        like adding, deleting, commenting, or viewing the movie collection. It
        also lets one generate a webpage for the movies or search the collection.

        Options:
        - Add a new movie.
        - Delete a movie.
        - Add/update or remove a pop-up comment.
        - Search for a movie by title.
        - Generate a webpage with the collection.

        """
        print(f"\n{YELLOW}{'☆' * 10}{RESET} VIEWERS FAVOURITE MOVIES {YELLOW}"
              f"{'☆' * 10}{RESET}")
        print(f"{GREEN}Add movies, delete them and add comments. See it all"
              f" on the website!{RESET}\n")
        menu_title = "Menu:"
        print(f"{menu_title}\n{YELLOW}{'‾' * len(menu_title)}{RESET}")

        while True:
            menu_options = {
                0: "Exit",
                1: "List movies",
                2: "Add movie",
                3: "Delete movie",
                4: "Update comment",
                5: "Search movie",
                6: "Generate website",
            }

            for key, val in menu_options.items():
                print(f"{YELLOW}{key}{RESET}. {val}")

            choice = input(f"{GREEN}\nPlease enter choice (0-6):{RESET} ")

            if choice == "0":
                print(f"{PURPLE}Thanks for using the MovieApp. See you next time!{RESET}")
                break
            elif choice == "1":
                self._command_list_movies()
            elif choice == "2":
                self.add_movie()
            elif choice == "3":
                self.delete_movie()
            elif choice == "4":
                self.update_movie()
            elif choice == "5":
                self.search_movie()
            elif choice == "6":
                self.generate_website()
            else:
                print(f"{RED}Movie title not found! Check your spelling and"
                      f" try again.{RESET}")
