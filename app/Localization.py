import numpy as np
 
def latlon_to_xy(lat, lon, lat0, lon0, R=6371000):
    """
    Convert latitude and longitude (in degrees) to local Cartesian coordinates (x, y) in meters,
    relative to a reference point (lat0, lon0). This uses an equirectangular approximation,
    which is reasonable for small areas.
    """
    lat0_rad = np.deg2rad(lat0)
    dlat = np.deg2rad(np.array(lat) - lat0)
    dlon = np.deg2rad(np.array(lon) - lon0)
    x = dlon * np.cos(lat0_rad) * R
    y = dlat * R
    return x, y
 
def xy_to_latlon(x, y, lat0, lon0, R=6371000):
    """
    Convert local Cartesian coordinates (x, y) in meters back to latitude and longitude (in degrees),
    using (lat0, lon0) as the reference.
    """
    lat = y / R * (180 / np.pi) + lat0
    lon = x / (R * np.cos(np.deg2rad(lat0))) * (180 / np.pi) + lon0
    return lat, lon
 
def localize_transmitter(receiver_lat, receiver_lon, doa_degs, R=6371000, offset_std=0.5):
    """
    Estimate the transmitter's location from DOA measurements collected at a single receiver.
    In a single-receiver scenario, every DOA line naturally passes through the receiver's location.
    To avoid this degeneracy (and mimic spatial separation or noise), we add a small random offset 
    to the receiver's coordinates for each measurement.
    
    For each measurement, the line is given by:
         y - y_R_i = tan(theta) * (x - x_R_i)
    where (x_R_i, y_R_i) is the receiver's (simulated) position for measurement i.
    
    Parameters:
      receiver_lat, receiver_lon : float
          Receiver's known latitude and longitude in degrees.
      doa_degs : list or array-like of floats
          List of DOA measurements in degrees (measured relative to east, where 0°=east, 90°=north).
      R : float, optional
          Earth's radius in meters.
      offset_std : float, optional
          Standard deviation (in meters) for the random offset added to the receiver's position 
          for each measurement (default is 0.5 m).
    
    Returns:
      transmitter_lat, transmitter_lon : float
          Estimated transmitter latitude and longitude in degrees.
      residuals : ndarray
          Sum of squared residuals from the least-squares solution.
    """
    # Choose a reference point slightly offset from the receiver to define our local coordinate system.
    lat0 = receiver_lat - 0.001  # about 0.001° offset (~111 m)
    lon0 = receiver_lon - 0.001
    # Convert the receiver's nominal position to local Cartesian coordinates.
    x_R_nom, y_R_nom = latlon_to_xy(receiver_lat, receiver_lon, lat0, lon0, R)
    
    N = len(doa_degs)
    A = np.zeros((N, 2))
    b_vec = np.zeros(N)
    
    # For each measurement, simulate a small random offset to the receiver position.
    for i, theta_deg in enumerate(doa_degs):
        theta_rad = np.deg2rad(theta_deg)
        # Simulate small offsets (in meters) for this measurement.
        delta_x = np.random.normal(0, offset_std)
        delta_y = np.random.normal(0, offset_std)
        x_R_i = x_R_nom + delta_x
        y_R_i = y_R_nom + delta_y
        
        # The line equation becomes:
        #   tan(theta) * x_T - y_T = tan(theta) * x_R_i - y_R_i
        A[i, :] = [np.tan(theta_rad), -1]
        b_vec[i] = np.tan(theta_rad) * x_R_i - y_R_i

    # Solve the over-determined system in a least-squares sense.
    p_est, residuals, rank, s = np.linalg.lstsq(A, b_vec, rcond=None)
    x_T, y_T = p_est
    # Convert the estimated local (x, y) back to latitude and longitude.
    transmitter_lat, transmitter_lon = xy_to_latlon(x_T, y_T, lat0, lon0, R)
    return transmitter_lat, transmitter_lon, residuals
 
# ----------------------------
# Example usage:
# ----------------------------
if __name__ == '__main__':
    # Set seed for reproducibility of the random offsets.
    np.random.seed(42)
    
    # Known receiver location (latitude, longitude in degrees)
    receiver_lat = 35.1456591
    receiver_lon = 33.4152348
    
    # Example DOA measurements (in degrees relative to east).
    # In an ideal, noise-free scenario with one receiver these would all point to the receiver,
    # but with simulated offsets they will yield a transmitter estimate different from the receiver.
    doa_degs = [181, 179, 174, 186, 189, 188, 180, 179, 175, 185, 178, 178, 182, 180]
    
    transmitter_lat, transmitter_lon, residuals = localize_transmitter(receiver_lat, receiver_lon, doa_degs)
    print("Estimated Transmitter Position:")
    print("  Latitude: ", transmitter_lat)
    print("  Longitude:", transmitter_lon)
    print(f"Copy: {transmitter_lat}, {transmitter_lon}")
    print("Least-Squares Residuals:", residuals)
