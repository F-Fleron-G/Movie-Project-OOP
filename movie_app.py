import requests
import random
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
                  f" successfully!{RESET}")

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
                      f"been successfully deleted.")
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

    def show_stats(self):
        """
        Shows off some fun facts about your movie collection.

        This method gives you an overview of your movies, including:
        - Average rating (so you know if your taste is more high-brow or low-key)
        - Median rating (to see where the “middle ground” lies in your collection)
        - Your top-rated movie(s) and bottom-rated movie(s), so you can brag or hide them.

        Use this feature to get a quick snapshot of how your collection stacks up!
        """
        movies = self._storage.list_movies()

        if not movies:
            print(f"{RED}Sorry, there are no movies available."
                  f" Please add one first.{RESET}")
            return

        ratings = []
        highest_rating = None
        lowest_rating = None
        highest_rated_movies = []
        lowest_rated_movies = []
        total_rating = 0

        for title, details in movies.items():
            rating = details.get('rating', 0)
            ratings.append(rating)
            total_rating += rating

            if highest_rating is None or rating > highest_rating:
                highest_rating = rating
                highest_rated_movies = [title]
            elif rating == highest_rating:
                if title not in highest_rated_movies:
                    highest_rated_movies.append(title)

            if lowest_rating is None or rating < lowest_rating:
                lowest_rating = rating
                lowest_rated_movies = [title]
            elif rating == lowest_rating:
                if title not in lowest_rated_movies:
                    lowest_rated_movies.append(title)

        average_rating = total_rating / len(ratings)
        ratings.sort()
        mid = len(ratings) // 2
        if len(ratings) % 2 == 0:
            median_rating = (ratings[mid - 1] + ratings[mid]) / 2
        else:
            median_rating = ratings[mid]

        stats_title = "Movie List Statistics:"
        print(f"\n{stats_title}\n{YELLOW}{'‾' * len(stats_title)}{RESET}")
        print(f"Average rating: {CYAN}{average_rating:.1f}{RESET}")
        print(f"Median rating: {CYAN}{median_rating:.1f}{RESET}")

        print("Best movie(s):", end=" ")
        for movie in highest_rated_movies:
            print(f"{YELLOW}{capitalize_movie_name(movie)}{RESET},"
                  f" {CYAN}{highest_rating}{RESET}", end=" / ")
        print()

        print("Worst movie(s):", end=" ")
        for movie in lowest_rated_movies:
            print(f"{YELLOW}{capitalize_movie_name(movie)}{RESET},"
                  f" {CYAN}{lowest_rating}{RESET}", end=" / ")
            print()
        print()

    def random_movie(self):
        """
        Feeling indecisive? Let fate choose a movie for you!

        This method picks a movie at random from your collection and displays its details.
        Perfect if you’re having a movie night but can’t decide what to watch.
        Take a chance—who knows, you might rediscover an old favorite!
        """
        movies = self._storage.list_movies()

        if not movies:
            print(f"{RED}No movies available.{RESET}")
            return

        title = random.choice(list(movies.keys()))
        details = movies[title]
        movie_rec_title = "Recommended Movie:"
        print(f"\n{movie_rec_title}\n{YELLOW}{'‾' * len(movie_rec_title)}{RESET}")
        print(f"{YELLOW}{capitalize_movie_name(title)}{RESET} ({details['year']}),"
              f" {CYAN}{details['rating']}{RESET}")
        print()

    def movies_sorted_by_rating(self):
        """
        Ranks your movies from legendary to... well, less legendary.

        This method sorts your entire collection by rating, from the highest rated
        (the crème de la crème) to the lowest rated (the “it was okay, I guess”).
        Quickly find out which flicks take the crown and which ones are still waiting
        for their big comeback.
        """
        movies = self._storage.list_movies()

        if not movies:
            print(f"{RED}No movies available to sort.{RESET}")
            return

        sorted_movies = sorted(movies.items(),
                               key=lambda item: item[1].get('rating', 0), reverse=True)

        ordered_rated_movies_title = "Movies Ordered by Rating:"
        print(f"\n{ordered_rated_movies_title}\n{YELLOW}"
              f"{'‾' * len(ordered_rated_movies_title)}{RESET}")

        for movie, details in sorted_movies:
            print(
                f"{YELLOW}{capitalize_movie_name(movie)}{RESET}"
                f" ({details['year']}), {CYAN}{details['rating']}{RESET}")
        print()

    def movies_sorted_by_year(self):
        """
        Travel through time with your movie collection.

        This method sorts all of your movies by their release year. Whether you choose
        to see the newest hits first or journey back to the classics, it’s a neat way
        to explore how your tastes have evolved—or stayed comfortingly old-school!
        """
        movies = self._storage.list_movies()

        if not movies:
            print(f"{RED}No movies available to sort.{RESET}")
            return

        sorted_movies = sorted(movies.items(), key=lambda item: item[1].get('year', 0))

        by_year_title = "Movies Sorted By Year:"
        print(f"\n{by_year_title}\n{YELLOW}{'‾' * len(by_year_title)}{RESET}")

        while True:
            order_choice = input(f"{GREEN}To sort from newest to oldest movies type: 'L'\n"
                                 f"To sort from oldest to newest movies type: 'E'\n{RESET}").strip().lower()
            if order_choice == 'l':
                sorted_movies.reverse()
                break
            elif order_choice == 'e':
                break
            else:
                print(f"{RED}Wrong input! Please enter either 'L' or 'E'.{RESET}")

        for movie, details in sorted_movies:
            year = details.get('year', 'N/A')
            rating = details.get('rating', 'N/A')
            print(f"{YELLOW}{capitalize_movie_name(movie)}{RESET} ({year}),"
                  f" {CYAN}{rating}{RESET}")
        print()

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
        Brings everything together in one interactive menu.

        This method offers a friendly menu where you can:
        - List all movies you’ve stored.
        - Add new flicks to your collection.
        - Delete any titles you’re no longer fond of.
        - Update notes (comments) on your movies.
        - Search for a movie by its title.
        - Check out some fun stats (like average ratings and best/worst movies).
        - Pick a random movie for those indecisive nights.
        - See your movies ranked by rating or sorted by year.
        - Finally, generate a cool-looking website that showcases your entire library!

        Just follow the on-screen instructions, choose a number, and have fun
        managing your personal movie empire!
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
                6: "Stats",
                7: "Random movie",
                8: "Movies sorted by rating",
                9: "Movies sorted by year",
                10: "Generate website"
            }

            for key, val in menu_options.items():
                print(f"{YELLOW}{key}{RESET}. {val}")

            choice = input(f"{GREEN}\nPlease enter choice (0-10):{RESET} ")

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
                self.show_stats()
            elif choice == "7":
                self.random_movie()
            elif choice == "8":
                self.movies_sorted_by_rating()
            elif choice == "9":
                self.movies_sorted_by_year()
            elif choice == "10":
                self.generate_website()
            else:
                print(f"{RED}Invalid Entry! Please enter a number from 0-10.{RESET}")
            print()
