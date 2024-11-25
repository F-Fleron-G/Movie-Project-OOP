import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
PURPLE = "\033[95m"
RESET = "\033[0m"


def normalize_movie_name(movie_name):
    """Normalizes the movie name by stripping whitespace and converting to lowercase."""
    return movie_name.strip().lower()


def capitalize_movie_name(movie_name):
    """Capitalizes the movie title to make it more readable."""
    return movie_name.strip().title()


class MovieApp:
    def __init__(self, storage):
        """
        Initializes the MovieApp with the specified storage.

        Args:
            storage: An instance of a class implementing the IStorage interface.
        """
        self._storage = storage
        self.api_url = "http://www.omdbapi.com/"
        self.api_key = "a942dd70"

    def add_movie(self):
        """
        Adds a movie to the collection by fetching data from the OMDb API.
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
        Shows all the movies stored in the app.
        If there are no movies, you'll get a friendly message about that too.
        """
        movies = self._storage.list_movies()
        if movies:
            for title, details in movies.items():
                print(f"{YELLOW}{capitalize_movie_name(title)}{RESET}: {details}\n")
        else:
            print(f"{RED}Oops! No movies found in the database.{RESET}")

    def delete_movie(self):
        """
        Allows the user to delete a movie by its title.
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
        Updates a movie's details in the database.
        """
        movies = self._storage.list_movies()
        movie_name = input(f"{GREEN}Enter the movie name:{RESET} ").strip()

        if movie_name not in movies:
            print(f"Movie {YELLOW}'{movie_name}'{RESET} not found!")
            return

        notes = input(f"{GREEN}Enter your notes for the movie:{RESET} ").strip()
        notes = notes[:100]

        movie_details = movies[movie_name]
        movie_details["notes"] = notes

        try:
            self._storage.update_movie(movie_name, movie_details)
            print(f"Notes for {YELLOW}'{movie_name}'{RESET} successfully updated!")
        except ValueError as e:
            print(f"{RED}Error updating movie: {e}{RESET}")

    def search_movie(self):
        """
        Search for a movie by its title and list all movies that contain the
        search term.
        """
        search_query = input(f"{GREEN}Enter the movie title to search:"
                             f"{RESET} ").strip()

        normalized_query = normalize_movie_name(search_query)

        movies = self._storage.list_movies()

        found_movies = []

        for title, details in movies.items():
            normalized_title = normalize_movie_name(title)

            if normalized_query in normalized_title:
                found_movies.append((title, details))

        if found_movies:
            print(f"\nFound movies matching {YELLOW}'{capitalize_movie_name(search_query)}'"
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
        try:
            with open('_static/index_template.html', 'r') as template_file:
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
        """Displays the introductory page with the menu options for the user."""
        print(f"\n{YELLOW}{'☆' * 10}{RESET} VIEWERS FAVOURITE MOVIES {YELLOW}"
              f"{'☆' * 10}{RESET}")
        print(f"{GREEN}Add movies, delete them and add comments. See it all"
              f" on the web!{RESET}\n")
        menu_title = "Menu:"
        print(f"{menu_title}\n{YELLOW}{'‾' * len(menu_title)}{RESET}")

        while True:
            menu_options = {
                0: "Exit",
                1: "List movies",
                2: "Add movie",
                3: "Delete movie",
                4: "Update movie",
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
