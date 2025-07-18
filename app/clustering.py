from sklearn.cluster import DBSCAN
import numpy as np
import random
import db.connect as connect
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BAND = 446

def setBand(band):
    """
    Set the band for clustering.
    
    Args:
        band (int): The band to set.
    """
    global BAND
    BAND = band
    
def getBand():
    """
    Get the current band for clustering.
    
    Returns:
        int: The current band.
    """
    global BAND
    return BAND

class SpeakerIdentifier:
    def __init__(self):
        """
        Initialize the SpeakerIdentifier class.
        
        Args:
            reference_time (float): The start time for DOA retrieval.
            conn: An object with a method `retrieve_text(start_time, end_time)` to fetch DOA data.
        """
        self.reference_time = datetime.now(ZoneInfo("Etc/GMT-1"))  # Reference time for DOA data
        # ****************
        # self.reference_time = datetime.fromisoformat("2025-04-03 13:56:55.489295+01:00")
        # ****************
        self.cluster_to_speaker = {}  # Map of cluster centroids to speaker IDs
        self.next_speaker_id = 1      # Counter for assigning unique speaker IDs
        print(f"Reference time: {self.reference_time}")
    

    def process_transcription(self, conn, start_time, end_time, wavFile, text=None):
        """
        Processes a transcription by identifying speakers based on DOA data.
        
        Args:
            start_time (float): Start time of the transcription relative to reference time.
            end_time (float): End time of the transcription relative to reference time.
        
        Returns:
            list: List of speaker IDs associated with this transcription.
        """
        
        print(f"SIUUUU: {text}")
        # Step 2: Retrieve DOA data from connection
        # print(f"Processing transcription from {start_time} to {end_time} with reference time {self.reference_time}")
        print(f"SELF REFERENCE TIME: {self.reference_time}")
        doa_data = connect.retreive_doa(conn, self.reference_time + timedelta(seconds=start_time), self.reference_time + timedelta(seconds=end_time))
        if not doa_data:
            print(f"No DOA data for interval {self.reference_time + timedelta(seconds=start_time)} to {self.reference_time + timedelta(seconds=end_time)} for text {text}")
            return []  # No DOA data for this interval
        eps = 5
        min_samples = 6
        
        # Step 3: Extract DOAs from retrieved data
        doa_array = np.array(doa_data).reshape(-1, 1)

        # Step 4: Apply DBSCAN clustering
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)  # Adjust parameters as needed
        cluster_labels = dbscan.fit_predict(doa_array)

        # self.plot_clusters_on_ax(ax, doa_array, cluster_labels)

        # print(f"SIUUUUUUUUUUUUUUUUUUUUU {doa_array}")
        # Step 5: Calculate centroids for each cluster
        unique_clusters = set(cluster_labels) - {-1}  # Ignore noise (-1)
        cluster_centroids = [
            np.mean(doa_array[cluster_labels == cluster]) for cluster in unique_clusters
        ]

        # Step 6: Match clusters to speakers
        transcription_speakers = []  # List of speakers for this transcription
        for centroid in cluster_centroids:
            matched = False
            for known_centroid, speaker_id in self.cluster_to_speaker.items():
                if abs(centroid - known_centroid) <= 10:  # Threshold for matching
                    transcription_speakers.append(speaker_id)
                    matched = True
                    break

            if not matched:
                # New speaker detected
                self.cluster_to_speaker[centroid] = self.next_speaker_id
                transcription_speakers.append(self.next_speaker_id)
                self.next_speaker_id += 1
        
        # print(f"SIUUUUUUUUUUUUUU {len(transcription_speakers)}")
        if len(transcription_speakers) > 1:
            self.process_transcription(conn, start_time, (start_time + end_time) / 2, wavFile)
            self.process_transcription(conn, (start_time + end_time) / 2, end_time, wavFile)
        else:
            speaker_id = transcription_speakers[0] if transcription_speakers else -1  # Default to -1 if no speakers detected
            speaker_centroid = None
            if speaker_id != -1:
                for centroid, spk_id in self.cluster_to_speaker.items():
                    if spk_id == speaker_id:
                        speaker_centroid = centroid
                        break
            print(f"Band is: {int(getBand())}")
            connect.insert_diarization(conn, start_time, end_time, speaker_id, wavFile, speaker_centroid, str(getBand()) + "Mhz")
            print(f"Speakers for Transcription: {transcription_speakers} start_time: {self.reference_time + timedelta(seconds=start_time)} end_time: {self.reference_time + timedelta(seconds=end_time)} data {doa_array} Text: {text}")
        
        # self.plot_final_clusters_on_ax(ax)


if __name__ == "__main__":
    # Initialize the SpeakerIdentifier class
    reference_time = 0.0  # Starting time
    # conn = connect.connect_to_database()
    identifier = SpeakerIdentifier()
    # mock_doa(conn)
    # data = []
    data = [
        289, 271, 260, 249, 253, 254, 161, 155, 153, 159, 161, 279, 142, 143, 143, 
        140, 135, 131, 115, 6, 5, 22, 30, 17, 16, 20, 27, 121, 120, 122, 139, 133, 
        333, 140, 139, 140, 140, 138, 138, 140, 139, 136, 133, 133, 135, 136, 135, 
        136, 137, 138, 136, 132, 326
    ]
    
    # result = cluster_and_visualize(data, 5, 5)
    # print("Cluster Labels:", result["cluster_labels"])
    # print("Centroids:", result["centroids"])
    
    values = np.sort(data)  # Sort the array
    differences = np.diff(values)  # Calculate differences between consecutive elements
    range_diff = np.ptp(values)  # Range: max - min
    std_dev = np.std(values)  # Standard deviation

    print("Array Values (sorted):", values)
    print("Differences between consecutive values:", differences)
    print("Range (max - min):", range_diff)
    print("Standard Deviation:", std_dev)

    # # Process transcriptions
    # transcription_1 = identifier.process_transcription(0.0, 0.5, "")  # Interval: 0.0 - 0.5
    # transcription_2 = identifier.process_transcription(2.0, 2.8, "")  # Interval: 1.0 - 2.0
    # transcription_3 = identifier.process_transcription(5.0, 7.0, "")  # Interval: 2.4 - 2.9
    # transcription_2 = identifier.process_transcription(2.0, 2.8, "")  # Interval: 1.0 - 2.0


    # print(f"Speakers for Transcription 1: {transcription_1}")
    # print(f"Speakers for Transcription 2: {transcription_2}")
    # print(f"Speakers for Transcription 3: {transcription_3}")
    # print(f"Cluster to Speaker Mapping: {identifier.cluster_to_speaker}")
