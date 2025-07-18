import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cdist

# Step 1: Load the DOA values from the text
doas = []
with open('/home/ubuntulaptop/UCY/Thesis/app/doa.txt', 'r') as file:
    for line in file:
        if line.startswith("DOA:"):
            doa_values = line.strip().split(":")[1].strip().strip('[]').split(',')
            doas.append([int(float(value)) for value in doa_values])

# Step 2: Flatten the DOA lists and use DBSCAN for clustering
all_doa = []
for doa_list in doas:
    all_doa.extend(doa_list)

# Reshape the data for clustering (DBSCAN expects a 2D array)
all_doa = np.array(all_doa).reshape(-1, 1)

# Apply DBSCAN clustering
eps = 10  # Adjust depending on your data
min_samples = 2  # Adjust depending on your data
dbscan = DBSCAN(eps=eps, min_samples=min_samples)
labels = dbscan.fit_predict(all_doa)

# Step 3: Organize the clusters and calculate centroids
clustered_doa = {}
for i, label in enumerate(labels):
    if label not in clustered_doa:
        clustered_doa[label] = []
    clustered_doa[label].append(all_doa[i][0])

# Function to compute the centroid of a cluster
def compute_centroid(cluster):
    return np.mean(cluster)

# Step 4: Merge clusters with centroids closer than the threshold
threshold = 10  # The distance threshold to merge clusters
centroids = {label: compute_centroid(doa_list) for label, doa_list in clustered_doa.items()}
labels_to_merge = []

# Compare each pair of clusters
for label1, centroid1 in centroids.items():
    for label2, centroid2 in centroids.items():
        if label1 != label2 and abs(centroid1 - centroid2) < threshold:
            # Mark the pair for merging
            if (label2, label1) not in labels_to_merge and (label1, label2) not in labels_to_merge:
                labels_to_merge.append((label1, label2))

# Merge the clusters
for label1, label2 in labels_to_merge:
    if label1 in clustered_doa and label2 in clustered_doa:
        # Combine the clusters
        clustered_doa[label1].extend(clustered_doa[label2])
        del clustered_doa[label2]  # Remove the merged cluster

# Step 5: Plotting the clusters
plt.figure(figsize=(8, 8))
ax = plt.subplot(111, projection='polar')

# Rotate the plot to make 0° (North) at the top
ax.set_theta_offset(-np.pi / 4)  # Set 180° to the top (facing South)
# ax.set_theta_direction(-1)       # Set angles to increase clockwise

# For plotting, we will assign different colors and markers for each cluster
markers = ['o', 'x', '^', 's', '*']
colors = ['blue', 'green', 'red', 'purple', 'orange']

# Iterate through each cluster and plot
for label, doa_list in clustered_doa.items():
    # Add the angle and distance data for each cluster
    cluster_angles = np.radians(doa_list)
    cluster_distances = [8] * len(doa_list)  # Dummy distance for plotting purposes
    ax.scatter(cluster_angles, cluster_distances, color=colors[label % len(colors)], 
               label=f"Cluster {label + 1}", marker=markers[label % len(markers)])

ax.set_rmax(20)  # Set radial limit slightly beyond the max distance

# Adding title and legend
ax.set_title("DOA Clusters with DBSCAN", y=1.1)
plt.legend(loc='upper right', bbox_to_anchor=(1, 1.1))

# Show the plot
plt.show()
