# Define time tolerance (in seconds)
time_tolerance = 0.5

# List to store combined output
combined_output = []
# Transcriptions list with start and end time in seconds, text
transcriptions = [
    (5.86, 9.48, "Harvard list number one."),
    (9.90, 12.68, "The birch canoe slid on the smooth planks."),
    (15.28, 17.82, "Glue the sheet to the dark blue background."),
    (20.40, 22.60, "It's easy to tell the depth of a well."),
    (25.84, 28.58, "These days a chicken leg is a rare dish."),
    (31.54, 34.06, "Rice is often served in round bowls."),
    (36.90, 39.58, "The juice of lemons makes fine punch."),
    (42.78, 45.58, "The box was thrown beside the parked truck."),
    (48.40, 51.28, "The hogs were fed chopped corn and garbage."),
    (54.32, 56.82, "Four hours of steady work faced us."),
    (60.02, 62.58, "Large size and stockings is hard to sell.")
]

# Diarization list with start and end time in seconds, speaker label
diarization = [
    (6.105, 7.759, "SPEAKER_00"),
    (10.375, 12.805, "SPEAKER_00"),
    (15.657, 18.036, "SPEAKER_00"),
    (20.787, 22.727, "SPEAKER_00"),
    (26.170, 28.769, "SPEAKER_00"),
    (31.857, 34.202, "SPEAKER_00"),
    (37.425, 39.704, "SPEAKER_00"),
    (43.315, 45.694, "SPEAKER_00"),
    (48.917, 51.516, "SPEAKER_00"),
    (54.689, 57.000, "SPEAKER_00"),
    (60.291, 62.670, "SPEAKER_00")
]

for trans_start, trans_end, trans_text in transcriptions:
    best_match = None
    min_time_diff = float("inf")
    
    for dia_start, dia_end, speaker in diarization:
        # Calculate the overlap within tolerance
        if (trans_start - time_tolerance) <= dia_end and (trans_end + time_tolerance) >= dia_start:
            # Find the time difference between transcription and diarization segments
            time_diff = abs((trans_start + trans_end) / 2 - (dia_start + dia_end) / 2)
            
            # Update if this diarization segment is the closest match within tolerance
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                best_match = {
                    "start_time": max(trans_start, dia_start),
                    "end_time": min(trans_end, dia_end),
                    "speaker": speaker,
                    "text": trans_text
                }

    # Add the best match (if found) to the combined output
    if best_match:
        combined_output.append(best_match)

# Display the combined output
for entry in combined_output:
    print(f"[{entry['start_time']:.2f}s -> {entry['end_time']:.2f}s] {entry['speaker']}: {entry['text']}")
