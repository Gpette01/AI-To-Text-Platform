import matplotlib.pyplot as plt
import numpy as np

# Cluster data
# cluster1 = [156, 136, 164, 166, 166, 166, 165]
# cluster2 = [246, 246, 245, 246, 246]
# cluster3 = [81, 78, 78, 78, 81, 78, 80, 92, 88]

# cluster1 = [104, 105, 106, 105, 105, 105, 104, 105, 105, 105, 105, 104, 104, 106, 105, 102, 101, 104, 104, 104, 106, 108, 104, 102, 102, 101, 101, 100, 100, 101, 101, 98]
# cluster2 = [128, 126, 124, 125, 127, 130, 131, 130, 129, 128, 130, 125, 135, 136, 136, 135, 135, 137, 137, 136, 136, 136, 135, 134, 134, 135, 134, 133, 131, 142, 143, 143, 140, 135, 131, 139, 133, 140, 139, 140, 140, 138, 138, 140, 139, 136, 133, 133, 135, 136, 135, 136, 137, 138, 136, 132]
# cluster3 = [190, 180, 181, 178, 173, 171, 174, 184, 180, 182, 186, 186, 182, 181, 181, 180, 178, 179, 180, 178, 178, 176, 174, 173, 167, 189]
cluster1 =  [80.0, 80.0, 82.0, 81.0, 82.0, 81.0, 81.0, 81.0, 82.0, 83.0, 82.0, 82.0, 82.0, 82.0, 82.0, 82.0, 82.0, 83.0, 85.0, 85.0, 85.0, 84.0, 84.0, 83.0, 82.0, 84.0, 81.0, 81.0, 81.0, 82.0, 80.0, 85.0, 85.0, 85.0, 84.0, 82.0, 82.0]
cluster2 = [131.0, 133.0, 131.0, 131.0, 132.0, 132.0, 131.0, 132.0, 132.0, 132.0, 133.0, 134.0, 135.0, 136.0, 135.0, 133.0, 132.0, 132.0, 131.0, 134.0, 131.0, 132.0, 132.0, 135.0, 131.0, 130.0, 130.0, 133.0, 133.0, 134.0, 134.0, 133.0, 134.0, 134.0, 134.0, 137.0, 140.0, 140.0, 145.0, 145.0, 141.0, 142.0, 142.0, 135.0, 133.0, 132.0, 130.0, 130.0, 130.0, 130.0, 130.0, 130.0, 130.0, 130.0, 130.0, 129.0, 131.0, 131.0, 132.0, 132.0, 134.0, 135.0, 135.0, 135.0, 134.0, 135.0, 134.0, 135.0, 138.0, 139.0]
cluster3 = [232.0, 226.0, 229.0, 233.0, 232.0, 229.0, 227.0, 227.0, 228.0, 222.0, 224.0, 228.0, 229.0, 229.0, 229.0, 229.0, 228.0, 229.0, 229.0, 230.0, 230.0, 229.0, 228.0, 229.0]

# Step 1: Modify the other two clusters to have value and distance (distance assumed as 5 for simplicity)
# new_angle=19
new_angle1 = 60
new_angle2 = 90
new_angle3 = 90
new_angle1 = 0
new_angle2 = 0
new_angle3 = 0
# print(np.mean(cluster3)+new_angle)

cluster1_modified = [(angle+new_angle1, 8) for angle in cluster1]
cluster2_modified = [(angle+new_angle2, 9) for angle in cluster2]
cluster3_modified = [(angle+new_angle3, 10) for angle in cluster3]
print(cluster1_modified)

# Step 2: Prepare the data for plotting
# Convert angles to radians (required for polar plots)
cluster1_angles, cluster1_distances = zip(*cluster1_modified)
cluster1_angles = np.radians(cluster1_angles)

cluster2_angles, cluster2_distances = zip(*cluster2_modified)
cluster2_angles = np.radians(cluster2_angles)

cluster3_angles, cluster3_distances = zip(*cluster3_modified)
cluster3_angles = np.radians(cluster3_angles)

# Step 3: Create polar plot
plt.figure(figsize=(8, 8))
ax = plt.subplot(111, projection='polar')

# Rotate the plot to make 0° (North) at the top
ax.set_theta_offset(-np.pi / 4)  # Set 180° to the top (facing South)
ax.set_theta_offset(0)  # Set 180° to the top (facing South)
# ax.set_theta_direction(-1)       # Set angles to increase clockwise

cluster4_angles=[80, 135, 225]
cluster4_distances=[8, 9, 10]
cluster4_angles = np.radians(cluster4_angles)

# Plot each cluster
ax.scatter(cluster1_angles, cluster1_distances, color='blue', label='Cluster 1', marker='o')
ax.scatter(cluster2_angles, cluster2_distances, color='green', label='Cluster 2', marker='x')
ax.scatter(cluster3_angles, cluster3_distances, color='red', label='Cluster 3', marker='^')
ax.scatter(cluster4_angles, cluster4_distances, color='black', label='Ground Truth', marker='s')

ax.set_rmax(20)  # Set radial limit slightly beyond the max distance



# Adding title and legend
ax.set_title("DOA Clusters", y=1.1)

# Displaying the legend
plt.legend(loc='upper right', bbox_to_anchor=(1, 1.1))

# Show the plot
plt.show()
