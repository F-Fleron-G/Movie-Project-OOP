from abc import ABC, abstractmethod


class IStorage(ABC):
    """
    A blueprint for any storage system that handles movies.
    This class defines the methods you need to implement to interact with
    the storage.
    """

    @abstractmethod
    def list_movies(self):
        """
        Lists all the movies in storage.
        Should return a collection (like a list or dict) of movies with their details.
        """
        pass

    @abstractmethod
    def add_movie(self, title: str, details: dict):
        """
        Adds a new movie to storage.

        Args:
            title (str): The name of the movie.
            details (dict): A dictionary containing movie details like year,
            rating, and poster.

        This method should handle saving all this info in storage.
        """
        pass

    @abstractmethod
    def delete_movie(self, title):
        """
        Removes a movie from storage.

        Args:
            title (str): The name of the movie to be deleted.

        If the movie doesn't exist, this method should handle it gracefully
        (e.g., raise an error or just ignore).
        """
        pass

    @abstractmethod
    def update_movie(self, title: str, details: dict):
        """
        Updates specific fields of an existing movie.

        Args:
            title (str): The name of the movie to update.
            details (dict): A dictionary containing the updated fields.
        """
        pass
