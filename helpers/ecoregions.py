import geopandas as gpd
from shapely.geometry import Point


def get_ecoregion(lon, lat):
    """
    Find ecoregion information for a single sample point.

    Parameters:
        lon (float): Longitude of the sample point.
        lat (float): Latitude of the sample point.

    Returns:
        dict: A dictionary containing the Bailey ecoregion and RESOLVE ecoregion IDs.
    """
    # Hardcoded paths to the shapefiles
    baileys_ecoregions_path = (
        "BaileyEcoregions/BaileysEcoregions/BaileysEcoregionsFull.shp"
    )
    resolve_ecoregions_path = (
        "resolveEcoregions/resolveEcoregions/resolveEcoregions.shp"
    )

    # Load the ecoregion shapefiles
    baileys_ecoregions = gpd.read_file(baileys_ecoregions_path)
    resolve_ecoregions = gpd.read_file(resolve_ecoregions_path)

    # Create a GeoDataFrame for the sample location
    sample_location = gpd.GeoDataFrame(
        {"geometry": [Point(lon, lat)]}, crs="EPSG:4326"
    )

    # Perform spatial joins to get ecoregion IDs
    sample_bailey = gpd.sjoin(
        sample_location, baileys_ecoregions, how="left", predicate="intersects"
    )
    sample_resolve = gpd.sjoin(
        sample_location, resolve_ecoregions, how="left", predicate="intersects"
    )

    # Extract relevant information
    bailey_id = (
        sample_bailey["bailey_id"].iloc[0] if not sample_bailey.empty else None
    )
    resolve_id = (
        sample_resolve["ECO_ID"].iloc[0] if not sample_resolve.empty else None
    )

    return {"bailey_id": bailey_id, "resolve_id": resolve_id}


result = get_ecoregion(-122.4194, 37.7749)
print(result)
