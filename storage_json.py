import json
from istorage import IStorage


class StorageJson(IStorage):
    """
    A JSON-based movie storage system.
    It reads from and writes to a JSON file to keep track of the movies.
    """

    def __init__(self, file_path):
        """
        Sets up the storage with a JSON file.

        Args:
            file_path (str): The file where the movie data is stored.
        """
        self.file_path = file_path

    def _read_movies(self):
        """
        Reads the movies from the JSON file.
        If the file doesn't exist or is empty, it starts fresh with an empty list.

        Returns:
            dict: A dictionary of all the movies.
        """
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def _write_movies(self, movies):
        """
        Saves the movie data back into the JSON file.

        Args:
            movies (dict): All the movies to save.
        """
        with open(self.file_path, 'w') as file:
            json.dump(movies, file, indent=4)

    def list_movies(self):
        """
        Gets all the movies in storage.

        Returns:
            dict: A dictionary with all the movie details.
        """
        return self._read_movies()

    def add_movie(self, title, details):
        """
        Adds a new movie to the JSON file.

        Args:
            title (str): Title of the movie.
            details (dict): A dictionary containing the movie details.
        """
        movies = self.list_movies()
        movies[title] = details
        self._write_movies(movies)

    def delete_movie(self, title):
        """
        Removes a movie from your collection.

        Args:
            title (str): The name of the movie to delete.

        Raises:
            ValueError: If the movie doesn't exist.
        """
        movies = self._read_movies()
        if title not in movies:
            raise ValueError(f"Sorry, '{title}' isn't in the collection."
                             f" Can't delete it.")
        del movies[title]
        self._write_movies(movies)

    def update_movie(self, title: str, details: dict):
        """
        Updates specific fields of an existing movie.

        Args:
            title (str): The name of the movie to update.
            details (dict): A dictionary containing the updated fields (e.g., notes).

        Raises:
            ValueError: If the movie doesn't exist.
        """
        movies = self._read_movies()
        if title not in movies:
            raise ValueError(f"'{title}' isn't in the collection. Can't update it.")

        movies[title].update(details)
        self._write_movies(movies)
