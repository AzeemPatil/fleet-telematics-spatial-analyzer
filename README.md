# Fleet Telematics & ADAS Event Spatial Analyzer

## Overview
This Data Engineering pipeline processes raw telemetry logs from commercial fleet vehicles. It isolates Advanced Driver Assistance Systems (ADAS) events—such as hard braking, lane departures, and forward collision warnings—and maps them to a spatial grid. The goal is to identify infrastructural "hotspots" (e.g., dangerous intersections or poorly marked highway curves) using spatial clustering algorithms.

## Architecture
1. **Scalable Ingestion:** Python pipeline designed to read massive, continuous telemetry logs in chunks to optimize memory usage.
2. **Spatial Clustering:** Utilizes Scikit-Learn's DBSCAN algorithm alongside GeoPandas to group coordinate-based events into distinct hazardous zones.
3. **Database Integration:** Outputs clustered spatial data into formats ready for Google BigQuery ingestion.
4. **Analytics:** Advanced SQL queries aggregating event severity, ranking hotspots, and calculating spatial risk scores.

## Tech Stack
* **Language:** Python (Pandas, GeoPandas, Scikit-Learn)
* **Database:** Google BigQuery (Geospatial GIS)
* **Concepts:** Spatial Clustering (DBSCAN), Batch Processing, Telemetry Data
