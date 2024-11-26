from storage.storage_json import StorageJson
from movie_app import MovieApp


def main():
    """
    This is where everything kicks off.
    We set up the storage (JSON in this case) and start the movie app.
    """
    storage = StorageJson('data/movies.json')
    app = MovieApp(storage)
    app.run()


if __name__ == "__main__":
    main()
