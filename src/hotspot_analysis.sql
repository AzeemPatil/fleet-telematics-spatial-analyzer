/* =============================================================================
Query: ADAS Hotspot Severity Ranking
Description: Aggregates clustered vehicle telemetry data to calculate a risk 
             score for specific spatial zones. Helps identify map areas requiring 
             updated metadata (e.g., missing speed limits, sharp curves).
Target Dialect: Google BigQuery Standard SQL
=============================================================================
*/

WITH ClusteredEvents AS (
    -- Base table outputted by the Python DBSCAN pipeline
    SELECT 
        hotspot_cluster_id,
        vehicle_id,
        event_type,
        severity,
        speed_kmh,
        ST_GEOGPOINT(longitude, latitude) AS event_geo,
        timestamp
    FROM 
        `fleet_telemetry_project.processed.clustered_hotspots`
),

HotspotAggregations AS (
    -- Aggregate events at the cluster level to define the hotspot
    SELECT 
        hotspot_cluster_id,
        -- Calculate the exact geographical center of the cluster
        ST_CENTROID(ST_UNION_AGG(event_geo)) AS cluster_center_geo,
        COUNT(vehicle_id) AS total_incidents,
        COUNT(DISTINCT vehicle_id) AS unique_vehicles_involved,
        ROUND(AVG(speed_kmh), 2) AS average_incident_speed,
        
        -- Count specific event types using conditional aggregation
        COUNTIF(event_type = 'hard_braking') AS hard_braking_count,
        COUNTIF(event_type = 'forward_collision_warning') AS collision_warning_count,
        
        -- Calculate an weighted severity score 
        -- (Critical = 3pts, High = 2pts, Medium = 1pt, Low = 0.5pts)
        SUM(
            CASE severity
                WHEN 'critical' THEN 3.0
                WHEN 'high' THEN 2.0
                WHEN 'medium' THEN 1.0
                WHEN 'low' THEN 0.5
                ELSE 0.0
            END
        ) AS total_severity_score
    FROM 
        ClusteredEvents
    GROUP BY 
        hotspot_cluster_id
)

-- Final Selection: Rank the most dangerous physical locations
SELECT 
    hotspot_cluster_id,
    ST_ASGEOJSON(cluster_center_geo) AS hotspot_coordinates,
    total_incidents,
    unique_vehicles_involved,
    average_incident_speed,
    hard_braking_count,
    collision_warning_count,
    total_severity_score,
    -- Rank hotspots by severity score to prioritize map updates
    RANK() OVER(ORDER BY total_severity_score DESC) as danger_rank
FROM 
    HotspotAggregations
WHERE 
    unique_vehicles_involved > 1 -- Ensure it's not just one bad driver
ORDER BY 
    danger_rank ASC;
