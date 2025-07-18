import sqlite3

from pathlib import Path
from datetime import timedelta

# Connect to the SQLite database
def connect_to_database():
    # db_name = "speech_analysis.db"  # Name of the SQLite database
    db_name = Path(__file__).resolve().parent / "speech_analysis.db"
    # print(db_name)
    try:
        connection = sqlite3.connect(db_name)
        print(f"Connected to database '{db_name}' successfully.")
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Insert data into the Transcription table
def insert_transcription(connection, timeStart, timeEnd, text, wavFile):
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO Transcription (timeStart, timeEnd, text, wavFile)
        VALUES (?, ?, ?, ?);
        """
        cursor.execute(insert_query, (timeStart, timeEnd, text, wavFile))
        connection.commit()
        # print(f"Inserted transcription record: {timeStart} - {timeEnd}")
    except sqlite3.Error as e:
        print(f"Error inserting into Transcription table: {e}")

# Insert data into the Diarization table
def insert_diarization(connection, timeStart, timeEnd, speaker, wavFile, avg_doa, band):
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO Diarization (timeStart, timeEnd, speaker, wavFile, avg_doa, band)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor.execute(insert_query, (timeStart, timeEnd, speaker, wavFile, avg_doa, band))
        connection.commit()
        # print(f"Inserted diarization record: {timeStart} - {timeEnd}")
    except sqlite3.Error as e:
        print(f"Error inserting into Diarization table: {e}")

def insert_doa(connection, time, doa):
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO DOA (time, doa)
        VALUES (?, ?);
        """
        cursor.execute(insert_query, (time,doa,))
        connection.commit()
        # print(f"Inserted DOA record: {doa}")
    except sqlite3.Error as e:
        print(f"Error inserting into DOA table: {e}")

# # Retreive text based on file from Transcription table
# def retreive_text(connection, wavFile):
#     try:
#         cursor = connection.cursor()
#         query = """
#         SELECT text, timeStart, timeEnd FROM Transcription WHERE wavFile = ?;
#         """
#         cursor.execute(query, (wavFile,))
#         results = cursor.fetchall()
#         return results  # Extract the text column
#     except sqlite3.Error as e:
#         print(f"Error retreiving text from Transcription table: {e}")
# Retreive text based on file from Transcription table
def retreive_text(connection, wavFile):
    try:
        cursor = connection.cursor()
        query = """
        SELECT DISTINCT tb1.text, tb1.timeStart, tb1.timeEnd, tb2.speaker, tb2.avg_doa, tb2.band
        FROM (
            SELECT * FROM Transcription 
            WHERE wavFile = ?
        ) AS tb1
        LEFT JOIN Diarization AS tb2 
            ON tb1.wavFile = tb2.wavFile 
            AND tb1.timeStart = tb2.timeStart 
            AND tb2.speaker != -1;
        """
        # print(query)
        cursor.execute(query, (wavFile,))
        results = cursor.fetchall()
        return results  # Extract the text column
    except sqlite3.Error as e:
        print(f"Error retreiving text from Transcription table: {e}")

# def retreive_doa(connection, start_time, end_time):
#     try:
#         cursor = connection.cursor()
#         query = """
#         SELECT doa 
#         FROM DOA WHERE time >= ? AND time <= ?;
#         """
#         cursor.execute(query, (start_time, end_time))
#         results = [row[0] for row in cursor.fetchall()]  # Extract the doa column
#         return results
#     except sqlite3.Error as e:
#         print(f"Error retrieving doa from DOA table: {e}")
def retreive_doa(connection, start_time, end_time):
    try:
        cursor = connection.cursor()
        query = """
        SELECT doa 
        FROM DOA WHERE time >= ? AND time <= ?;
        """
        cursor.execute(query, (start_time, end_time))
        results = [row[0] for row in cursor.fetchall()]  # Extract the doa column

        print(f"DOA RESULTS BEFORE PROCESSING {results}")
        
        # Step 1: Count leading zeros
        leading_zeros = 0
        while leading_zeros < len(results) and results[leading_zeros] == 0:
            leading_zeros += 1

        # Step 2: Count trailing zeros
        trailing_zeros = 0
        while trailing_zeros < len(results) and results[-(trailing_zeros + 1)] == 0:
            trailing_zeros += 1

        # Step 3: Handle both leading and trailing zeros
        if leading_zeros > 0 and trailing_zeros > 0:
            # Remove both leading and trailing zeros
            results = results[leading_zeros:len(results)-trailing_zeros]
            print(f"REMOVING BOTH LEADING AND TRAILING ZEROS {results}")
        
        # Step 4: Handle leading zeros only
        elif leading_zeros > 0:
            # Remove leading zeros
            results = results[leading_zeros:]
            print(f"REMOVING LEADING ZEROS {results}")
            
            # Query more data from the end and add non-zero values to the end
            additional_end_time = end_time + timedelta(seconds=100)  # Extend by 100 seconds
            additional_query = """
            SELECT doa 
            FROM DOA WHERE time > ? AND time <= ?;
            """
            cursor.execute(additional_query, (end_time, additional_end_time))
            additional_results = [row[0] for row in cursor.fetchall()]
            results.extend([val for val in additional_results if val != 0][:leading_zeros])
            print(f"ADDING VALUES TO THE END {results}")

        # Step 5: Handle trailing zeros only
        elif trailing_zeros > 0:
            # Remove trailing zeros
            results = results[:-trailing_zeros]
            print(f"REMOVING TRAILING ZEROS {results}")
            
            # Query more data from the start and add non-zero values to the beginning
            additional_start_time = start_time - timedelta(seconds=100)  # Extend by 100 seconds
            additional_query = """
            SELECT doa 
            FROM DOA WHERE time >= ? AND time < ?;
            """
            cursor.execute(additional_query, (additional_start_time, start_time))
            additional_results = [row[0] for row in cursor.fetchall()]
            results = [val for val in additional_results if val != 0][:trailing_zeros] + results
            print(f"ADDING VALUES TO THE BEGINNING {results}")

        # *************
        with open("doa.txt", "a") as f:
            f.write(f"DOA: {results}\n")
        # *************
        return results
    except sqlite3.Error as e:
        print(f"Error retrieving doa from DOA table: {e}")




# Example Usage
if __name__ == "__main__":
    # Connect to the database
    connection = connect_to_database()
    
    if connection:
        # Insert example data into Transcription table
        insert_transcription(connection, "00:00:00", "00:00:10", "Hello, world!", "audio1.wav")
        insert_transcription(connection, "00:00:10", "00:00:20", "This is a test.", "audio1.wav")

        # Insert example data into Diarization table
        insert_diarization(connection, "00:00:00", "00:00:05", "Speaker 1", "audio1.wav")
        insert_diarization(connection, "00:00:05", "00:00:10", "Speaker 2", "audio1.wav")

        # Close the connection
        connection.close()
        print("Database connection closed.")
