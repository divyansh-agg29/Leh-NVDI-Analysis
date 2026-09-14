
"""
Satellite image preprocessing utilities.

This module contains functions for preparing satellite imagery
before vegetation-index calculations.
"""

import ee



def mask_clouds(image, dataset_name):
    """
    Mask cloud and cloud-shadow pixels from a Landsat image.

    Parameters
    ----------
    image : ee.Image
        Input Landsat image.

    dataset_name : str
        Name of the satellite dataset.

    Returns
    -------
    ee.Image
        Image with cloud and cloud-shadow pixels masked.
    """

    # Check that the dataset is supported.
    if not dataset_name.lower().startswith("landsat"):
        raise ValueError(
            f"Unsupported dataset for cloud masking: {dataset_name}"
        )

    # Select the quality-assurance band.
    qa = image.select("QA_PIXEL")

    # Create masks for unwanted pixel conditions.
    dilated_cloud = qa.bitwiseAnd(1 << 1).eq(0)
    cirrus = qa.bitwiseAnd(1 << 2).eq(0)
    cloud = qa.bitwiseAnd(1 << 3).eq(0)
    cloud_shadow = qa.bitwiseAnd(1 << 4).eq(0)

    # Combine all masks.
    clear_mask = (
        dilated_cloud
        .And(cirrus)
        .And(cloud)
        .And(cloud_shadow)
    )

    # Apply the mask to the image.
    return image.updateMask(clear_mask)



def mask_snow(image, dataset_name):
    """
    Mask snow-covered pixels from a Landsat image.

    Parameters
    ----------
    image : ee.Image
        Input Landsat image.

    dataset_name : str
        Name of the satellite dataset.

    Returns
    -------
    ee.Image
        Image with snow pixels masked.
    """

    # Validate the dataset.
    if not dataset_name.lower().startswith("landsat"):
        raise ValueError(
            f"Unsupported dataset for snow masking: "
            f"{dataset_name}"
        )

    # Select the quality-assurance band.
    qa = image.select("QA_PIXEL")

    # Bit 5 indicates snow.
    snow_free = qa.bitwiseAnd(1 << 5).eq(0)

    # Apply the snow mask.
    return image.updateMask(snow_free)



def apply_reflectance_scaling(image, dataset_name):
    """
    Apply Landsat Collection 2 Level 2 surface
    reflectance scaling.

    Parameters
    ----------
    image : ee.Image
        Input Landsat image.

    dataset_name : str
        Name of the satellite dataset.

    Returns
    -------
    ee.Image
        Image with scaled surface reflectance bands.
    """

    # Validate the dataset.
    if not dataset_name.lower().startswith("landsat"):
        raise ValueError(
            f"Unsupported dataset for reflectance scaling: "
            f"{dataset_name}"
        )

    # Select surface reflectance bands.
    optical_bands = image.select("SR_B.*")

    # Apply Landsat Collection 2 Level 2 scaling.
    scaled_optical = (
        optical_bands
        .multiply(0.0000275)
        .add(-0.2)
    )

    # Replace the original optical bands.
    return image.addBands(
        scaled_optical,
        overwrite=True
    )


def preprocess_collection(collection, dataset_name):
    """
    Apply all preprocessing steps to an image collection.

    Parameters
    ----------
    collection : ee.ImageCollection
        Input satellite image collection.

    dataset_name : str
        Name of the satellite dataset.

    Returns
    -------
    ee.ImageCollection
        Preprocessed image collection.
    """

    # Step 1: Mask clouds and cloud shadows.
    collection = collection.map(
        lambda image: mask_clouds(
            image,
            dataset_name
        )
    )

    # Step 2: Mask snow-covered pixels.
    collection = collection.map(
        lambda image: mask_snow(
            image,
            dataset_name
        )
    )

    # Step 3: Apply reflectance scaling.
    collection = collection.map(
        lambda image: apply_reflectance_scaling(
            image,
            dataset_name
        )
    )

    return collection