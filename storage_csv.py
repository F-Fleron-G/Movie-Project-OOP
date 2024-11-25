import csv
from istorage import IStorage


class StorageCsv(IStorage):
    """
    Handles movie storage in a CSV file format. Each movie is stored as a row
    with columns for title, rating, and year. Implements the IStorage interface.
    """

    def __init__(self, file_name: str):
        """
        Initializes the CSV storage with a file name.

        Args:
            file_name (str): The name of the CSV file to store the movies.
        """
        self.file_name = file_name

    def _read_movies(self) -> dict:
        """
        Reads the movies from the CSV file and returns them as a dictionary.

        Returns:
            dict: A dictionary of movies with titles as keys.
        """
        try:
            with open(self.file_name, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                movies: dict[str, dict[str, float | int]] = {}

                for row in reader:
                    assert isinstance(row, dict)

                    title: str = row['title']
                    rating: float = float(row['rating'])
                    year: int = int(row['year'])

                    movies[title] = {'rating': rating, 'year': year}

                return movies
        except FileNotFoundError:
            return {}

    def _write_movies(self, movies: dict) -> None:
        """
        Writes the movies dictionary to the CSV file.

        Args:
            movies (dict): A dictionary of movies to write to the CSV file.
        """
        with open(self.file_name, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'rating', 'year']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for title, details in movies.items():
                writer.writerow({
                    'title': title,
                    'rating': details['rating'],
                    'year': details['year']
                })

    def list_movies(self) -> dict:
        """
        Returns a dictionary of dictionaries that
        contains the movies information in the database.

        Returns:
            dict: A dictionary of movies.
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

    def delete_movie(self, title: str) -> None:
        """
        Deletes a movie from the database by title.

        Args:
            title (str): The title of the movie to delete.
        """
        movies = self._read_movies()
        if title in movies:
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
