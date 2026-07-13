import mysql.connector
from mysql.connector import errorcode
from dotenv import dotenv_values


def show_films(cursor, title):
    """Display film, director, genre, and studio information."""
    cursor.execute(
        """
        SELECT
            film.film_name AS Name,
            film.film_director AS Director,
            genre.genre_name AS Genre,
            studio.studio_name AS Studio
        FROM film
        INNER JOIN genre
            ON film.genre_id = genre.genre_id
        INNER JOIN studio
            ON film.studio_id = studio.studio_id
        ORDER BY film.film_name;
        """
    )

    films = cursor.fetchall()

    print(f"\n-- {title} --")

    for film in films:
        print(
            "Film Name: {}\n"
            "Director: {}\n"
            "Genre: {}\n"
            "Studio: {}\n".format(
                film[0],
                film[1],
                film[2],
                film[3]
            )
        )


secrets = dotenv_values(".env")

config = {
    "user": secrets["USER"],
    "password": secrets["PASSWORD"],
    "host": secrets["HOST"],
    "database": secrets["DATABASE"],
    "raise_on_warnings": True
}

db = None
cursor = None

try:
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    # Display the original records
    show_films(cursor, "DISPLAYING FILMS")

    # Insert a new film
    cursor.execute(
        """
        INSERT INTO film
            (film_name, film_releaseDate, film_runtime,
             film_director, studio_id, genre_id)
        VALUES
            (
                'Us',
                '2019',
                116,
                'Jordan Peele',
                (SELECT studio_id
                 FROM studio
                 WHERE studio_name = 'Universal Pictures'),
                (SELECT genre_id
                 FROM genre
                 WHERE genre_name = 'Horror')
            );
        """
    )

    db.commit()
    show_films(cursor, "DISPLAYING FILMS AFTER INSERT")

    # Change Alien from SciFi to Horror
    cursor.execute(
        """
        UPDATE film
        SET genre_id = (
            SELECT genre_id
            FROM genre
            WHERE genre_name = 'Horror'
        )
        WHERE film_name = 'Alien';
        """
    )

    db.commit()
    show_films(cursor, "DISPLAYING FILMS AFTER UPDATE")

    # Delete Gladiator
    cursor.execute(
        """
        DELETE FROM film
        WHERE film_name = 'Gladiator';
        """
    )

    db.commit()
    show_films(cursor, "DISPLAYING FILMS AFTER DELETE")

except mysql.connector.Error as err:
    if db is not None:
        db.rollback()

    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("The supplied username or password are invalid.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("The specified database does not exist.")
    else:
        print(err)

finally:
    if cursor is not None:
        cursor.close()

    if db is not None and db.is_connected():
        db.close()