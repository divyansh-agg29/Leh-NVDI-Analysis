"""
TIF file preview generation.

"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import TwoSlopeNorm


def create_ndvi_preview(
    tif_path: str | Path,
    output_png_path: str | Path,
    title: str,
    display_mode: str = "contrast",
) -> Path:
    """
    Create a readable PNG preview from an NDVI GeoTIFF.

    display_mode:
        - "comparison": fixed NDVI scale from -1 to +1
        - "contrast": adaptive scale based on the image values
    """

    tif_path = Path(tif_path)
    output_png_path = Path(output_png_path)

    output_png_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(tif_path) as src:
        ndvi = src.read(1).astype("float32")
        nodata = src.nodata
        bounds = src.bounds

    # Convert NoData pixels to NaN.
    if nodata is not None:
        ndvi = np.where(ndvi == nodata, np.nan, ndvi)

    valid_pixels = ndvi[np.isfinite(ndvi)]

    if valid_pixels.size == 0:
        raise ValueError(f"No valid NDVI pixels found in: {tif_path}")

        # Select colour scale.
    if display_mode == "comparison":
        # Full theoretical NDVI range.
        vmin = -1.0
        vmax = 1.0

    elif display_mode == "contrast":
        # Adaptive scale for inspecting one image.
        vmin = float(np.percentile(valid_pixels, 2))
        vmax = float(np.percentile(valid_pixels, 98))

        vmin = max(-1.0, vmin)
        vmax = min(1.0, vmax)

        if vmax <= vmin:
            vmin = -1.0
            vmax = 1.0

    else:
        raise ValueError(
            "display_mode must be one of: "
            "'contrast', 'comparison'"
        )

    fig, ax = plt.subplots(figsize=(10, 7))

    image = ax.imshow(
        ndvi,
        cmap="RdYlGn",
        vmin=vmin,
        vmax=vmax,
        extent=[
            bounds.left,
            bounds.right,
            bounds.bottom,
            bounds.top,
        ],
        origin="upper",
        interpolation="nearest",
    )

    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")

    # Subtle grid for geographic orientation.
    ax.grid(
        True,
        linestyle="--",
        linewidth=0.5,
        alpha=0.35,
    )

    # Keep the geographic proportions correct.
    ax.set_aspect("equal", adjustable="box")

    colorbar = fig.colorbar(
        image,
        ax=ax,
        shrink=0.85,
        pad=0.03,
    )

    colorbar.set_label("NDVI", rotation=270, labelpad=15)

    # Show the actual colour range used for this image.
    ax.text(
        0.01,
        0.02,
        f"Colour scale: {vmin:.2f} to {vmax:.2f}",
        transform=ax.transAxes,
        fontsize=8,
        bbox={
            "facecolor": "white",
            "alpha": 0.75,
            "edgecolor": "none",
        },
    )

    fig.tight_layout()

    fig.savefig(
        output_png_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output_png_path


def create_ndvi_change_preview(
    tif_path: str | Path,
    output_png_path: str | Path,
    title: str,
) -> Path:
    """
    Create a red-white-green preview from an NDVI change GeoTIFF.

    Negative values:
        Vegetation decrease

    Values near zero:
        Little or no change

    Positive values:
        Vegetation increase
    """

    tif_path = Path(tif_path)
    output_png_path = Path(output_png_path)

    output_png_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(tif_path) as src:
        change = src.read(1).astype("float32")
        nodata = src.nodata
        bounds = src.bounds

    # Mark NoData as NaN.
    if nodata is not None:
        change = np.where(change == nodata, np.nan, change)

    valid_pixels = change[np.isfinite(change)]

    if valid_pixels.size == 0:
        raise ValueError(f"No valid change pixels found in: {tif_path}")

    # Use a symmetric scale around zero.
    # This ensures that equal increases and decreases
    # receive equally strong colours.
    max_change = float(
        np.percentile(np.abs(valid_pixels), 98)
    )

    max_change = max(max_change, 0.01)

    vmin = -max_change
    vmax = max_change

    # Red = decrease, white = zero, green = increase.
    cmap = plt.get_cmap("RdYlGn").copy()
    cmap.set_bad("lightgrey")

    norm = TwoSlopeNorm(
        vmin=vmin,
        vcenter=0.0,
        vmax=vmax,
    )

    fig, ax = plt.subplots(figsize=(10, 7))

    image = ax.imshow(
        change,
        cmap=cmap,
        norm=norm,
        extent=[
            bounds.left,
            bounds.right,
            bounds.bottom,
            bounds.top,
        ],
        origin="upper",
        interpolation="nearest",
    )

    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel("Longitude (degrees)")
    ax.set_ylabel("Latitude (degrees)")

    ax.grid(
        True,
        linestyle="--",
        linewidth=0.5,
        alpha=0.35,
    )

    ax.set_aspect("equal", adjustable="box")

    colorbar = fig.colorbar(
        image,
        ax=ax,
        shrink=0.85,
        pad=0.03,
    )

    colorbar.set_label(
        "NDVI change",
        rotation=270,
        labelpad=15,
    )

    ax.text(
        0.01,
        0.02,
        f"Colour scale: {vmin:.2f} to {vmax:.2f}",
        transform=ax.transAxes,
        fontsize=8,
        bbox={
            "facecolor": "white",
            "alpha": 0.75,
            "edgecolor": "none",
        },
    )

    fig.tight_layout()

    fig.savefig(
        output_png_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output_png_path


if __name__ == "__main__":

    RUN_DIR = Path(
        "data/processed/run_20260915_233901"
    )

    PREVIEW_DIR = RUN_DIR / "previews"
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)


    create_ndvi_preview(
        tif_path=RUN_DIR / "ndvi_middle_2008.tif",
        output_png_path=(
            PREVIEW_DIR / "ndvi_middle_2008_comparison.png"
        ),
        title="NDVI — 2008",
        display_mode="comparison",
    )

    # --------------------------------------------------
    # NDVI change — 1990 to 2025
    # --------------------------------------------------

    create_ndvi_change_preview(
        tif_path=RUN_DIR / "ndvi_change_1990_2025.tif",
        output_png_path=(
            PREVIEW_DIR / "ndvi_change_1990_2025.png"
        ),
        title="NDVI Change — 1990 to 2025",
    )

    print(f"Previews saved to: {PREVIEW_DIR}")