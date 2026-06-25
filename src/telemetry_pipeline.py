import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.cluster import DBSCAN
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_telemetry_stream(file_path, chunk_size=10000):
    """
    Reads large telemetry logs in chunks to simulate scalable batch ingestion.
    """
    logging.info(f"Starting chunked ingestion for {file_path}")
    chunks = []
    
    # Iterate through file in manageable memory chunks
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Filter for actionable ADAS events (ignore regular pings if they existed)
        adas_events = chunk[chunk['event_type'].notnull()]
        chunks.append(adas_events)
        
    # Concatenate processed chunks
    full_df = pd.concat(chunks, ignore_index=True)
    logging.info(f"Processed {len(full_df)} total ADAS events.")
    return full_df

def apply_spatial_clustering(df, eps_degrees=0.0005, min_samples=2):
    """
    Uses DBSCAN ML algorithm to cluster GPS points that are physically close.
    eps_degrees of 0.0005 is roughly 50 meters.
    """
    logging.info("Applying DBSCAN spatial clustering to find event hotspots...")
    
    # Extract coordinates for clustering
    coords = df[['latitude', 'longitude']].values
    
    # Run DBSCAN
    # Note: For massive global datasets, Haversine metric with radians is preferred. 
    # Using default Euclidean here for localized regional processing.
    db = DBSCAN(eps=eps_degrees, min_samples=min_samples).fit(coords)
    
    # Assign cluster labels back to dataframe (-1 means unclustered/noise)
    df['hotspot_cluster_id'] = db.labels_
    
    # Filter out noise to only keep established hotspots
    hotspots_df = df[df['hotspot_cluster_id'] != -1].copy()
    logging.info(f"Identified {len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)} unique spatial hotspots.")
    
    return hotspots_df

def export_spatial_data(df, output_path):
    """Converts Pandas DataFrame to a spatial GeoJSON for GIS processing."""
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    gdf.to_file(output_path, driver='GeoJSON')
    logging.info(f"Pipeline complete. Spatial data exported to {output_path}")

if __name__ == "__main__":
    INPUT_CSV = "../data/telemetry_sample.csv"
    OUTPUT_GEOJSON = "../data/clustered_hotspots.geojson"
    
    # Run pipeline
    raw_telemetry = process_telemetry_stream(INPUT_CSV, chunk_size=5) # Small chunk size to demonstrate functionality on sample
    clustered_data = apply_spatial_clustering(raw_telemetry)
    export_spatial_data(clustered_data, OUTPUT_GEOJSON)
