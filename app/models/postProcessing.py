import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the CSV files for each model.
csv_files = {
    'FasterWhisper': 'transcription_evaluation_fasterWhisper.csv',
    'Wav2Vec': 'transcription_evaluation_wav2vec.csv',
    'WhisperCPP': 'transcription_evaluation_whispercpp.csv',
    'Faster-Whisper \nDistil': 'transcription_evaluation_distil.csv',  # Replace with actual filename
    'Normal-Turbo': 'transcription_evaluation_nromalturbo.csv'        # Replace with actual filename
}

# Create a dictionary to store the averaged metrics for each model.
averages = {}

# Compute the mean values for each required metric.
for model, file in csv_files.items():
    try:
        df = pd.read_csv(file)
        # Calculate averages; adjust column names if they differ.
        avg_elapsed = df['Elapsed_Time'].mean()
        avg_WER = df['WER'].mean()
        avg_MER = df['MER'].mean()
        avg_WIL = df['WIL'].mean()
        
        averages[model] = {
            'elapsed_time': avg_elapsed,
            'WER': avg_WER,
            'MER': avg_MER,
            'WIL': avg_WIL
        }
    except Exception as e:
        print(f"Error processing file {file} for model {model}: {e}")

if not averages:
    raise ValueError("No data available; please check your CSV file paths and column names.")

plt.rcParams.update({'font.size': 14})

# -----------------------------------------------------------
# Graph 1: Average Elapsed Time for Each Model (unchanged)
# -----------------------------------------------------------
models = list(averages.keys())
avg_elapsed_times = [averages[model]['elapsed_time'] for model in models]

plt.figure(figsize=(10, 6))
bars = plt.bar(models, avg_elapsed_times, color='skyblue')
plt.title('Average Elapsed Time by Model')
plt.xlabel('Models')
plt.ylabel('Average Elapsed Time')

# Annotate each bar with its value (4 decimal places)
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        height,
        f'{height:.4f}',
        ha='center',
        va='bottom'
    )

plt.tight_layout()
plt.savefig('average_elapsed_time.png')
plt.show()

# -----------------------------------------------------------
# Graph 2: Average WER, MER, and WIL by Metric (Grouped by Metric)
# -----------------------------------------------------------
metrics = ['WER', 'MER', 'WIL']
n_metrics = len(metrics)
n_models = len(models)

# x positions for metric groups
x = np.arange(n_metrics)

# Width of each individual bar within a group
bar_width = 0.12

# Use a more powerful/vibrant colormap (tab10 has bright, distinct colors)
colors = plt.cm.tab10(np.linspace(0, 1, n_models))

fig, ax = plt.subplots(figsize=(12, 7))

# For each model, determine its offset in each metric group and plot its bars.
for i, model in enumerate(models):
    # Compute horizontal offset so that bars for each model are centered within the group.
    offset = (i - (n_models - 1) / 2) * bar_width * 1.3
    # Gather values for the current model across all metrics.
    metric_values = [averages[model][metric] for metric in metrics]
    # Position of bars for the current model.
    positions = x + offset
    bars = ax.bar(positions, metric_values, bar_width, color=colors[i], label=model, edgecolor='black')
    
    # Annotate each bar with its value (4 decimal places).
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2,
            height,
            f'{height:.4f}',
            ha='center',
            va='bottom'
        )

# Set up x-axis labels (one label per metric group)
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.set_xlabel('Metric')
ax.set_ylabel('Average Score')
ax.set_title('Average WER, MER, and WIL by Metric (Grouped by Metric)')

# Add legend mapping each model to its color.
ax.legend(title="Models")

plt.tight_layout()
plt.savefig('average_metrics_grouped_by_metric.png')
plt.show()
