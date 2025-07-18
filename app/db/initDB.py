import sqlite3

# Create a new SQLite database and initialize the tables
def initialize_database():
    db_name = "speech_analysis.db"  # Name of the SQLite database
    connection = sqlite3.connect(db_name)
    print(f"Database '{db_name}' created successfully.")
    
    # Create Transcription table
    create_transcription_table_query = """
    CREATE TABLE IF NOT EXISTS Transcription (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timeStart TEXT NOT NULL,
        timeEnd TEXT NOT NULL,
        text TEXT NOT NULL,
        wavFile TEXT NOT NULL
    );
    """
    connection.execute(create_transcription_table_query)
    print("Table 'Transcription' created successfully.")
    
    # Create Diarization table
    create_diarization_table_query = """
    CREATE TABLE IF NOT EXISTS Diarization (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timeStart TEXT NOT NULL,
        timeEnd TEXT NOT NULL,
        speaker TEXT NOT NULL,
        wavFile TEXT NOT NULL,
        avg_doa FLOAT NOT NULL,
        band TEXT NOT NULL
    );
    """
    connection.execute(create_diarization_table_query)
    print("Table 'Diarization' created successfully.")
    
    create_doa_table_query = """
    CREATE TABLE IF NOT EXISTS DOA (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT NOT NULL,
        doa INTEGER NOT NULL
    );
    """
    connection.execute(create_doa_table_query)
    print("Table 'DOA' created successfully.")
    
    # Close the connection
    connection.close()

initialize_database()
