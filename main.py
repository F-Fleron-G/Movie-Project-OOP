from movie_app import MovieApp
from storage_json import StorageJson


def main():
    """
    This is where everything kicks off.
    We set up the storage (JSON in this case) and start the movie app.
    """
    storage = StorageJson('movies.json')
    app = MovieApp(storage)
    app.run()


if __name__ == "__main__":
    main()
