import sqlite3

# Connect to SQLite database (create it if not exists)
conn = sqlite3.connect('Theater1.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        selected_movie TEXT,
        amount_paid INTEGER DEFAULT 0, 
        FOREIGN KEY (selected_movie) REFERENCES movies(title)
    )
''')

cursor.execute('''CREATE TABLE IF NOT EXISTS movies (
                     id INTEGER PRIMARY KEY,
                     title TEXT,
                     tickets_available INTEGER,
                     ticket_price INTEGER 
                 )''')

# Insert movies only if they don't exist already
movies_to_insert = [('Jab We Met', 100, 150), ('Sultan', 150, 200), ('Crew', 120, 180),
                    ('Heera Mandi', 80, 220), ('Geeta Govinda', 200, 250)]
for movie_title, tickets, price in movies_to_insert:
    cursor.execute("SELECT id FROM movies WHERE title=?", (movie_title,))
    existing_movie = cursor.fetchone()
    if not existing_movie:
        cursor.execute("INSERT INTO movies (title, tickets_available, ticket_price) VALUES (?, ?, ?)", (movie_title, tickets, price))
        print(f"Added movie: {movie_title}")
    else: 
        print(f"Movie '{movie_title}' already exists, skipping insertion.")

# Fetch all movies from the database
cursor.execute("SELECT * FROM movies")
movies = cursor.fetchall()

# Display movie list with ticket prices to the user
print("Welcome..")
print("List of movies available:")
for movie in movies:
    print(f"{movie[0]}. {movie[1]} - Ticket Price: Rs.{movie[3]}")

print("\nWelcome to Theatre Management System")

conn.commit()

# Function to register a new user
def register_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    cursor.execute('INSERT INTO users (username, password, selected_movie) VALUES (?, ?, NULL)', (username, password))
    conn.commit()
    print("User registered successfully!")


# Function to select a movie for a user and check ticket availability
def select_movie(user_id):
    movie_id = int(input("Enter the movie ID you want to select: "))
    cursor.execute("SELECT title, tickets_available, ticket_price FROM movies WHERE id=?", (movie_id,))
    selected_movie = cursor.fetchone()
    if selected_movie:
        if selected_movie[1] > 0:  # Check if tickets are available
            cursor.execute('UPDATE users SET selected_movie=? WHERE id=?', (selected_movie[0], user_id))
            cursor.execute('UPDATE movies SET tickets_available=tickets_available-1 WHERE id=?', (movie_id,))
            ticket_price = selected_movie[2]
            print(f"Ticket Price: ${ticket_price}")
            amount_paid = int(input("Enter the exact amount to pay: "))
            if amount_paid == ticket_price:  # Check if payment amount is correct
                cursor.execute('UPDATE users SET amount_paid=amount_paid+? WHERE id=?', (amount_paid, user_id))
                conn.commit()
                print(f"Movie '{selected_movie[0]}' added to your account.")
                print("Payment successful!")
            else:
                print("Incorrect payment amount. Payment failed.")
                
        else:
            print("Tickets for this movie are not available.")
            
    else:
        print("Invalid movie ID.")


# Comment out for experimental purpose...
# def select_movie(user_id):
#     selected_movies = []
#     total_amount = 0

#     while True:
#         movie_id = int(input("Enter the movie ID you want to select (or 0 to finish): "))
#         if movie_id == 0:
#             break

#         cursor.execute("SELECT title, tickets_available, ticket_price FROM movies WHERE id=?", (movie_id,))
#         selected_movie = cursor.fetchone()
#         if selected_movie:
#             if selected_movie[1] > 0:  # Check if tickets are available
#                 selected_movies.append((selected_movie[0], selected_movie[2]))  # Store movie name and price
#                 total_amount += selected_movie[2]  # Add movie price to total amount
#                 cursor.execute('UPDATE users SET selected_movie=? WHERE id=?', (selected_movie[0], user_id))
#                 cursor.execute('UPDATE movies SET tickets_available=tickets_available-1 WHERE id=?', (movie_id,))
#                 print(f"Movie '{selected_movie[0]}' added to your account.")
#             else:
#                 print("Tickets for this movie are not available.")
#         else:
#             print("Invalid movie ID.")

#     # Display selected movies and total amount
#     print("\nSelected Movies:")
#     for movie_name, price in selected_movies:
#         print(f"{movie_name} - Price: ${price}")
#     print(f"Total Amount: ${total_amount}")

#     # Payment process
#     amount_paid = int(input("Enter the exact amount to pay: "))
#     if amount_paid == total_amount:  # Check if payment amount is correct
#         cursor.execute('UPDATE users SET amount_paid=amount_paid+? WHERE id=?', (amount_paid, user_id))
#         for movie_name, _ in selected_movies:
#             cursor.execute('INSERT INTO user_movie_mapping (user_id, movie_name, amount_paid) VALUES (?, ?, ?)', (user_id, movie_name, amount_paid))
#         conn.commit()
#         print("Payment successful!")
#     else:
#         print("Incorrect payment amount. Payment failed.")



# Function to check if tickets are available for a movie
def check_ticket_availability():
    movie_id = int(input("Enter the movie ID to check ticket availability: "))
    cursor.execute("SELECT title, tickets_available FROM movies WHERE id=?", (movie_id,))
    movie_info = cursor.fetchone()
    if movie_info:
        if movie_info[1] > 0:
            print(f"Tickets are available for '{movie_info[0]}'")
        else:
            print(f"Tickets for '{movie_info[0]}' are sold out.")
    else:
        print("Invalid movie ID.")
        

def cancel_ticket(user_id):
    cursor.execute("SELECT selected_movie FROM users WHERE id=?", (user_id,))
    selected_movie = cursor.fetchone()
    if selected_movie:
        cursor.execute("SELECT id, tickets_available, ticket_price FROM movies WHERE title=?", (selected_movie[0],))
        movie_info = cursor.fetchone()
        if movie_info:
            cursor.execute("UPDATE movies SET tickets_available=tickets_available+1 WHERE id=?", (movie_info[0],))
            cursor.execute("UPDATE users SET selected_movie=NULL WHERE id=?", (user_id,))
            cursor.execute("SELECT amount_paid FROM users WHERE id=?", (user_id,))
            amount_paid = cursor.fetchone()[0]
            cursor.execute("UPDATE users SET amount_paid=0 WHERE id=?", (user_id,))
            conn.commit()
            print(f"Ticket for '{selected_movie[0]}' cancelled.")
            print(f"Refunded amount: Rs.{amount_paid}")
        else:
            print("Selected movie not found in the database.")
    else:
        print("No ticket found to cancel.")


def get_selected_movie_info(user_id):
    cursor.execute("SELECT users.id, users.username, movies.title, movies.tickets_available, movies.ticket_price FROM users INNER JOIN movies ON users.selected_movie = movies.title WHERE users.id=?", (user_id,))
    selected_movie_info = cursor.fetchone()
    if selected_movie_info:
        print("\nSelected Movie Information:")
        print(f"User ID: {selected_movie_info[0]}")
        print(f"Username: {selected_movie_info[1]}")
        print(f"Selected Movie: {selected_movie_info[2]}")
        print(f"Tickets Available: {selected_movie_info[3]}")
        print(f"Ticket Price: ${selected_movie_info[4]}")
    else:
        print("No movie selected by the user.")
    

# Function to login
def login_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    cursor.execute('SELECT id FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    if user:
        print("Login successful!")
        return user[0]  # Return the user ID
    else:
        print("Invalid username or password.")
        return None  # Return None if login fails

# Main menu
while True:
    print("\n1. Register\n2. Login\n3. Check Ticket Availability\n4. Cancel Ticket\n5. Get Selected Movie Info\n6. Exit")
    choice = input("Choose option: ")
    if choice == '1':
        register_user()
    elif choice == '2':
        user_id = login_user()
        if user_id:
            select_movie(user_id)  # Pass the user ID for movie selection
    elif choice == '3':
        check_ticket_availability()
    elif choice == '4':
        user_id = login_user()  # Login again to get the user ID
        if user_id:
            cancel_ticket(user_id)  # Pass the user ID for canceling ticket
    elif choice == '5':
        user_id = login_user()  # Login again to get the user ID
        if user_id:
            get_selected_movie_info(user_id)  # Pass the user ID for fetching selected movie info
    elif choice == '6':
        print("Exiting...Thank You For Your Time")
        break
    else:
        print("Invalid choice!")



# Close database connection
cursor.close()
conn.close()
