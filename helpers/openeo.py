import openeo
import logging
import rasterio
import numpy as np
from shapely.geometry import box

# Get the logger instance from app.py
logger = logging.getLogger("my_app_logger")



def get_data(longitude, latitude, buffer_size=0.0001):
    try:
        # Step 1: Connect to the OpenEO backend
        connection = openeo.connect("openeo.dataspace.copernicus.eu")
        connection.authenticate_oidc()

        # Step 2: Define the bounding box around the point of interest
        bounding_box = {
            "west": longitude - buffer_size,
            "east": longitude + buffer_size,
            "south": latitude - buffer_size,
            "north": latitude + buffer_size,
        }

        # Step 3: Load the WorldCover collection
        datacube = connection.load_collection(
            "ESA_WORLDCOVER_10M_2021_V2",
            spatial_extent=bounding_box,
            bands=["MAP"],  # Specify the correct band name
        )

        # Step 4: Download the data as a GeoTIFF
        output_file = "landcover_point.tif"
        datacube.download(output_file, format="GTIFF")
        logger.info("Downloaded the land cover data to '%s'", output_file)
        land_use_info = extract_land_use(output_file)
        logger.info(land_use_info)
        
        return {"status": "Download complete", "file": output_file, "land_use_info" : land_use_info}

    except Exception as e:
        logger.error("Error occurred while downloading data: %s", str(e))
        return {"status": "Error", "message": str(e)}
        
def extract_land_use(tif_file):
    # Define LCCS codes and their corresponding land use classes
    lccs_mapping = {
        10: "Tree cover",
        20: "Shrubland",
        30: "Grassland",
        40: "Cropland",
        50: "Built-up",
        60: "Bare/sparse vegetation",
        70: "Snow and Ice",
        80: "Permanent water bodies",
        90: "Herbaceous wetland",
        95: "Mangroves",
        100: "Moss and lichen"
    }

    try:
        # Step 1: Read the GeoTIFF file
        with rasterio.open(tif_file) as src:
            land_cover_data = src.read(1)  # Read the first band (MAP)
        
        # Step 2: Extract unique land cover classes
        unique_classes = np.unique(land_cover_data)

        # Step 3: Get the first class if available
        if unique_classes.size > 0:
            first_class_code = unique_classes[0]
            first_land_use = lccs_mapping.get(first_class_code, "Unknown")
            logger.info("First extracted land use class: %s", first_land_use)
            return first_land_use
        else:
            logger.warning("No land cover classes found.")
            return "No data"

    except Exception as e:
        logger.error("Error occurred while extracting land use data: %s", str(e))
        return None