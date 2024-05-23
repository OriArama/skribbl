import socket
import threading
import sqlite3
import time
import random
import os
import words
from scapy.all import *

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

# Define global variables
# (These variables are used throughout the code)
number_of_connected_clients = 0  # Tracks the number of connected clients
is_game_available = True  # Indicates if the game is available to join
connected_players = []  # Stores sockets of connected players

start_game_function_call_count = 0  # Counter for the start_game function calls
list_words = words.words  # List of words used in the game
chosen_word = ""  # The word chosen for the game round
initial_time = 10  # Initial time for the game round
remaining_time = initial_time  # Remaining time for the game round
count_players_finish_timer = 0  # Counter for players who finished timer
timer_started = False  # Flag indicating if the timer has started
number_of_players_that_guessed_correct = 0  # Number of players who guessed correctly
number_of_player_limits_to_start_the_game = 3  # Number of players required to start the game
players_names = []  # List of players' names
players_who_guessed_right = []  # List of players who guessed correctly

event_restart_timer = threading.Event()  # Event for restarting the timer
event_all_players_finish_timer = threading.Event()  # Event for when all players finish timer
finish_game_thread_event = threading.Event()  # Event for finishing the game thread

# Generate a single symmetric key for all clients
shared_key = Fernet.generate_key()
cipher_suite = Fernet(shared_key)


def refresh():
    """
    Reset all global variables to their initial values.
    """
    global connected_players, start_game_function_call_count, list_words, chosen_word, remaining_time, \
        count_players_finish_timer, timer_started, number_of_players_that_guessed_correct, \
        number_of_player_limits_to_start_the_game, players_names, players_who_guessed_right, is_game_available, \
        number_of_connected_clients

    # refresh global variables
    connected_players = []
    start_game_function_call_count = 0
    list_words = words.words
    chosen_word = ""
    remaining_time = initial_time
    count_players_finish_timer = 0
    timer_started = False
    number_of_players_that_guessed_correct = 0
    number_of_player_limits_to_start_the_game = 3
    players_names = []
    players_who_guessed_right = []
    number_of_connected_clients = 0

    # Clear events
    event_restart_timer.clear()
    event_all_players_finish_timer.clear()
    finish_game_thread_event.clear()

    # Create players table and reset game availability
    create_table()
    is_game_available = True


def encrypt_key_with_client_public_key(client_public_key, shared_key):
    """
    Encrypt the shared key with the client's public key.

    Args:
    - client_public_key: Client's public key
    - shared_key: Shared symmetric key

    Returns:
    - ciphered_key: Encrypted shared key
    """
    ciphered_key = client_public_key.encrypt(
        shared_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphered_key


def decrypt(encrypted_data):
    """
    Decrypt encrypted data.

    Args:
    - encrypted_data: Data to decrypt

    Returns:
    - decrypted_data: Decrypted data
    """
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode('utf-8')
    return decrypted_data


def encrypt(data):
    """
    Encrypt data.

    Args:
    - data: Data to encrypt

    Returns:
    - encrypted_data: Encrypted data
    """
    encrypted_data = cipher_suite.encrypt(data.encode('utf-8'))
    return encrypted_data


def get_first_data(client_socket, client_address):
    """
    Handle initial data exchange with the client.

    Args:
    - client_socket: Client socket
    - client_address: Client address
    """
    global remaining_time
    global count_players_finish_timer
    global number_of_connected_clients
    # Create a new connection and cursor within the thread
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()
    name = ""
    monster = ""
    flag = False

    while True:  # Change to an infinite loop
        try:
            data = decrypt(client_socket.recv(1464))
            if not data:
                break  # If no data received, break out of the loop
            if data.startswith("name: "):
                name = data[6:]
                cursor.execute("SELECT COUNT(*) FROM players WHERE name = ?", (name,))
                result = cursor.fetchone()[0]
                if result == 1:
                    client_socket.send(encrypt("already used"))
                    client_socket.recv(1464)
                    name = ""
                elif ',' in name:
                    client_socket.send(encrypt("invalid name"))
                    client_socket.recv(1464)
                    name = ""
                else:
                    client_socket.send(encrypt("ok"))
                    client_socket.recv(1464)

            elif data.startswith("monster: "):
                monster = data[9:]
            elif data == "quit":
                print("Client requested to quit.")
                number_of_connected_clients = number_of_connected_clients - 1
                client_socket.close()
                break  # If the client sends a "quit" message, break out of the loop
        except Exception as e:
            print(f"An error occurred: {e}")

        if name != "" and monster != "":
            flag = True
            client_socket.send(encrypt("You can now close the app"))  # Send the close message
            client_socket.recv(1464)
            break  # If name and monster data are received, break out of the loop

    if flag:
        cursor.execute("INSERT INTO players (ip_address, port, name, character, points) VALUES (?, ?, ?, ?, 0)", (
            client_address[0], client_address[1], name, monster))
        conn.commit()
        cursor.execute("SELECT name FROM players")
        names = cursor.fetchall()
        cursor.execute("SELECT character FROM players")
        monsters = cursor.fetchall()
        index = 0
        for name_from_table in names:
            client_socket.send(
                encrypt(f"Player joins,{name_from_table[0]},{monsters[index][0]}"))
            client_socket.recv(1464)
            index = index + 1
        send_message_to_all_clients(f"Player joins,{name},{monster}", client_socket)
        connected_players.append(client_socket)
        if len(connected_players) >= number_of_player_limits_to_start_the_game:
            if initial_time == remaining_time:
                send_message_to_all_clients(f"Timer, {str(remaining_time)}", "")
                thread_remaining_time = threading.Thread(target=set_remaining_time)
                thread_remaining_time.start()
            else:
                client_socket.send(encrypt(f"Timer, {str(remaining_time)}"))
        conn.close()
        thread2 = threading.Thread(target=get_messages, args=(client_socket,))
        thread2.start()
        thread2.join()
        event_all_players_finish_timer.wait()
        start_game()


def set_remaining_time():
    """
    Set the remaining time until the game starts and manage the timer.
    """
    global remaining_time
    global timer_started

    timer_started = True
    while remaining_time > 0 and not event_restart_timer.is_set():
        time.sleep(1)
        remaining_time = remaining_time - 1
    if event_restart_timer.is_set():
        remaining_time = initial_time
        event_restart_timer.clear()
        timer_started = False


def start_game():
    """
    Start the game and manage game rounds.
    """
    global start_game_function_call_count
    global players_names
    global finish_game_thread_event
    global is_game_available
    if start_game_function_call_count == 0:
        start_game_function_call_count = 1
    else:
        return
    is_game_available = False
    last_round = False
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM players")
    players_names = cursor.fetchall()
    for i in range(2):
        for name in players_names:
            print(players_names)
            if i == 1 and name == players_names[len(players_names) - 1]:
                last_round = True
            thread3 = None
            for index in range(len(players_names)):
                message = ""
                if index == 0:
                    message = "You are the drawer"
                    connected_players[index].send(encrypt(message))
                    connected_players[index].recv(1464)
                    random_elements = random.sample(list_words, 3)
                    connected_players[index].send(
                        encrypt(f"Words,{random_elements[0]},{random_elements[1]},{random_elements[2]}"))
                    thread3 = threading.Thread(target=get_messages, args=(connected_players[index],))
                    thread3.start()
                else:
                    message = "You are a guesser"
                    connected_players[index].send(encrypt(message))
                    connected_players[index].recv(1464)
                    thread3 = threading.Thread(target=get_messages, args=(connected_players[index],))
                    message = f"{name[0]} is drawing"
                    connected_players[index].send(encrypt(message))
                    connected_players[index].recv(1464).decode("utf-8")
                    thread3.start()
            thread3.join()
            if finish_game_thread_event.is_set():
                finish_game_thread_event.clear()
            connected_players.append(connected_players.pop(0))
            if len(players_names) == 1:
                print(1111)
                break
            if not last_round:
                for j in range(len(connected_players)):
                    connected_players[j].send(encrypt("continue"))
                    connected_players[j].recv(1464)
        if len(players_names) == 1:
            print(1122)
            break
    if len(players_names) == 1:
        connected_players[0].send(encrypt("The last player"))
        connected_players[0].recv(1464)

    else:
        cursor.execute('''
                    SELECT name
                    FROM players
                    ORDER BY points DESC;
                    ''')
        # Fetch all rows from the result set
        winner = cursor.fetchone()
        for j in range(len(connected_players)):
            connected_players[j].send(encrypt("show the winner"))
            connected_players[j].recv(1464)
            connected_players[j].send(encrypt(winner[0]))
            connected_players[j].recv(1464)

    conn.close()
    refresh()
    return


def get_messages(client_socket):
     """
    Receive and process messages from the client.

    Args:
    - client_socket: Client socket
    """
    global count_players_finish_timer
    global chosen_word
    global number_of_players_that_guessed_correct
    global finish_game_thread_event
    global players_who_guessed_right
    while True:
        try:
            message = decrypt(client_socket.recv(1464))
        except:
            finish_game_thread_event.wait()
            print("Break")
            break
        conn = sqlite3.connect('players.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM players WHERE ip_address = ? AND port = ?;",
                       (client_socket.getpeername()[0], client_socket.getpeername()[1]))
        name = cursor.fetchone()[0]
        cursor.execute("SELECT character FROM players WHERE ip_address = ? AND port = ?;",
                       (client_socket.getpeername()[0], client_socket.getpeername()[1]))
        monster = cursor.fetchone()[0]
        if message.startswith("message_chat: "):
            message = message[14:]
            if chosen_word != "":
                guessed_time_encrypted = client_socket.recv(1464)
                guessed_time = int(decrypt(guessed_time_encrypted))
                if message.upper() == chosen_word.upper():
                    send_message_to_all_clients(f"Solve,{name},{monster},guessed the word", "")
                    guesser_points = int(guessed_time / 10) + 1
                    cursor.execute("UPDATE players SET points = points + ? WHERE ip_address = ? AND port = ?;",
                                   (guesser_points, client_socket.getpeername()[0], client_socket.getpeername()[1]))
                    cursor.execute("UPDATE players SET points = points + 5 WHERE ip_address = ? AND port = ?;",
                                   (connected_players[0].getpeername()[0], connected_players[0].getpeername()[1]))
                    # Commit the changes to the database
                    conn.commit()
                    number_of_players_that_guessed_correct = number_of_players_that_guessed_correct + 1
                    players_who_guessed_right.append(client_socket)
                    if number_of_players_that_guessed_correct == len(connected_players) - 1:
                        send_message_to_all_clients(f"Finish game round", "")
                else:
                    message_to_send = f"message: name: {name} monster: {monster} text: {message}"
                    send_message_to_all_clients(message_to_send, client_socket)
            else:
                message_to_send = f"message: name: {name} monster: {monster} text: {message}"
                send_message_to_all_clients(message_to_send, client_socket)
        elif message.startswith("quit"):
            message_to_send = f"remove ,{name},{monster}"
            send_message_to_all_clients(message_to_send, client_socket)
            remove_player_when_timer(client_socket)
            client_socket.close()
            break
        elif message.startswith("Timer finished"):
            client_socket.send(encrypt("Close app"))
            client_socket.recv(1464).decode("utf-8")
            count_players_finish_timer = count_players_finish_timer + 1
            if count_players_finish_timer == len(connected_players):
                event_all_players_finish_timer.set()
            break
        elif message.startswith("DRAWING") or message.startswith("Clear painting"):
            send_message_to_all_clients(message, client_socket)
        elif message.startswith("Word"):
            lst = message.split(',')
            chosen_word = lst[1]
            send_message_to_all_clients("Start Timer game", "")
        elif message.startswith("Game round finish"):
            client_socket.send(encrypt("Game word: " + chosen_word))
            client_socket.recv(1464)

            cursor.execute('''
            SELECT name, character, points
            FROM players
            ORDER BY points DESC;
            ''')
            # Fetch all rows from the result set
            rows = cursor.fetchall()
            for row in rows:
                name, character, points = row
                client_socket.send(
                    encrypt(f"{character},{name},{points}"))
                client_socket.recv(1464)
            client_socket.send(encrypt("stop"))
            client_socket.recv(1464)
        elif message == "Finish current results":
            chosen_word = ""
            number_of_players_that_guessed_correct = 0
            finish_game_thread_event.set()
            players_who_guessed_right = []
            break
        elif message == "Drawer_disconnected":
            remove_player_when_game(client_socket)
            send_message_to_all_clients("Finish game round", client_socket)
            client_socket.close()
            break
        elif message == "Guesser_disconnected":
            remove_player_when_game(client_socket)
            client_socket.close()
            if len(players_names) == 1:
                send_message_to_all_clients("Finish game round", client_socket)
            elif number_of_players_that_guessed_correct == len(connected_players) - 1:
                if client_socket in players_who_guessed_right:
                    send_message_to_all_clients(f"Left, {name} left", client_socket)
                    number_of_players_that_guessed_correct = number_of_players_that_guessed_correct - 1
                    players_who_guessed_right.remove(client_socket)
                else:
                    send_message_to_all_clients("Finish game round", client_socket)
            else:
                send_message_to_all_clients(f"Left, {name} left", client_socket)


def send_message_to_all_clients(message, who_not_to_send):
     """
    Send a message to all clients except one.

    Args:
    - message: Message to send
    - who_not_to_send: Client socket to exclude from recipients
    """
    for index in range(len(connected_players)):
        try:
            if who_not_to_send != connected_players[index]:
                connected_players[index].send(encrypt(message))
        except Exception as e:
            print(f"An error occurred while broadcasting to a client: {e}")


def remove_player_when_game(client_socket):
    """
    Remove a player from the game when they disconnect.

    Args:
    - client_socket: Client socket to remove
    """
    global players_names
    global number_of_connected_clients
    try:
        conn = sqlite3.connect('players.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM players WHERE ip_address = ? AND port = ?;",
                       (client_socket.getpeername()[0], client_socket.getpeername()[1]))
        name = cursor.fetchone()
        players_names.remove(name)
        cursor.execute("DELETE FROM players WHERE ip_address = ? AND port = ?;",
                       (client_socket.getpeername()[0], client_socket.getpeername()[1]))
        connected_players.remove(client_socket)
        number_of_connected_clients = number_of_connected_clients-1
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"An error occurred while removing the player from the database: {e}")


def remove_player_when_timer(client_socket):
    """
    Remove a player from the game when they disconnect during the waiting room.

    Args:
    - client_socket: Client socket to remove
    """
    global number_of_connected_clients
    try:
        conn = sqlite3.connect('players.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE ip_address = ? AND port = ?;",
                       (client_socket.getpeername()[0], client_socket.getpeername()[1]))
        connected_players.remove(client_socket)
        number_of_connected_clients = number_of_connected_clients-1
        if len(connected_players) < number_of_player_limits_to_start_the_game and timer_started is True:
            event_restart_timer.set()
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"An error occurred while removing the player from the database: {e}")


def create_table():
    """
    Create the 'players' table if it doesn't exist.
    """
    if os.path.exists('players.db'):
        # Remove the database file
        os.remove('players.db')

    # Create a new connection and cursor
    conn = sqlite3.connect('players.db')
    cursor = conn.cursor()

    # Define the SQL statement to create the "players" table
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY,
        ip_address TEXT,
        port TEXT,
        name TEXT,
        character TEXT,
        points INTEGER
    );
    '''

    # Execute the SQL statement to create the table
    cursor.execute(create_table_sql)

    # Commit the changes
    conn.commit()


def client_request(server_port):
    """
    Have an open thread in all times to see UDP messages of clients and respond to them
    """
    data = subprocess.check_output('ipconfig').decode('iso-8859-1')
    my_ip = [line for line in data.split('\n') if line.find('IPv4 Address') >= 0][0][37:].split(' ')[1]  # machine IP
    text = "Server Hello \n" + my_ip + "\n" + str(server_port)
    text = text.encode('utf-8')
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    port = int(server_port)

    while True:
        data = sniff(count=1, filter="udp and dst 255.255.255.255")  # braodcast
        a = data[0].show(dump=True)
        try:
            if "Client" in a:
                content = a[a.index("Client"):len(a) - 2]
                client_ip = re.findall('\d+.\d+.\d+.\d+', content)[0]
                client_port = re.findall(r'\d+', content)[-1]
                addr = (client_ip, int(client_port))
                sock.sendto(text, addr)
        except Exception as e:
            print(e)
            pass


def open_port():
    """
    Find the first free port and return it
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_server_shutdown_if_no_clients():
    """
    Start a timer thread to shut down the server if no clients are connected.
    """
    global server_socket, number_of_connected_clients
    while True:

        # Wait for 30 seconds
        time.sleep(30)

        # Check if there are no connected clients
        if number_of_connected_clients == 0:
            time.sleep(60)
            if number_of_connected_clients == 0:
                print("No clients connected within the timeout period. Shutting down server...")
                server_socket.close()  # Close the server socket
                break


if __name__ == "__main__":
    # Create the "players" table if it doesn't exist
    create_table()
    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_port = open_port()
    server_address = ('0.0.0.0', server_port)
    server_socket.bind(server_address)
    server_socket.listen()

    print("Server is listening on {}:{}...".format(server_address[0], server_address[1]))

    thread0 = threading.Thread(target=client_request, args=(server_port,), daemon=True)
    thread0.start()

    # Start the timer thread
    timer_thread = threading.Thread(target=start_server_shutdown_if_no_clients)
    timer_thread.start()
    while True:
        try:
            # Wait for a connection
            print("Waiting for a client to connect...")
            client_socket, client_address = server_socket.accept()
            print("Client connected from {}:{}".format(client_address[0], client_address[1]))
            number_of_connected_clients = number_of_connected_clients+1
            # Send the encrypted shared symmetric key to the client
            client_public_key_pem = client_socket.recv(4096)
            client_public_key = serialization.load_pem_public_key(client_public_key_pem)
            encrypted_key = encrypt_key_with_client_public_key(client_public_key, shared_key)
            client_socket.sendall(encrypted_key)

            if not is_game_available:
                client_socket.send(encrypt("Not available"))
                client_socket.recv(1464)
                client_socket.close()
            else:
                client_socket.send(encrypt("Available"))
                client_socket.recv(1464)

                # Handle initial data for the client in a separate thread
                thread1 = threading.Thread(target=get_first_data, args=(client_socket, client_address), daemon=True)
                thread1.start()
        except Exception as e:
            break
