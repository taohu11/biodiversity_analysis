import rasterio
import numpy as np
import geopandas as gpd
from skimage.transform import resize
from rasterio.features import geometry_mask

# Read the area raster
with rasterio.open(r'F:\TAO\36_Australia\Area\Calculate TIF meters\Calculate TIF meters\rasters\biodiversity_30_area.tif') as src:
    area = src.read(1)
    area_meta = src.meta

# Read land use data in 1990
with rasterio.open(r'F:\TAO\36_Australia\Landuse\landuse_1990_project_clip.tif') as src:
    landuse1990 = src.read(1)

# Define the species
species = 'Acrobates_pygmaeus'

# Read the standard raster data
with rasterio.open(r'F:\TAO\36_Australia\biodiversity_30.tif') as src:
    biodiversity_standard = src.read(1)
    R = src.meta
    size1 = biodiversity_standard.shape

# get the information of raster
info = src.meta

# Read habitat suitability data
biodiversity_name = f'F:\\TAO\\36_Australia\\mammals\\{species}\\{species}_historic_baseline_1990_AUS_5km_EnviroSuit.tif'
with rasterio.open(biodiversity_name) as src:
    biodiversity = src.read(1).astype(float)
    biodiversity[biodiversity == 255] = np.nan

# Resample
bio_resample = resize(biodiversity, size1, order=0, preserve_range=True).astype(float)

# Read the boundary of species
shp_path = f'F:\\TAO\\36_Australia\\mammals_models\\{species}\\mammals_{species}_Extent_of_occurrence_buffered.shp'
shp = gpd.read_file(shp_path)

# Create the mask
mask = geometry_mask([shp.geometry[0]], transform=src.transform, invert=True, out_shape=bio_resample.shape)
bio_resample[~mask] = 0


bio_resample[biodiversity_standard == 255] = 255

# 输出TIF文件 (需安装 gdal 或 rasterio)
# output_path = f'F:\\TAO\\36_Australia\\mammals\\{species}\\{species}_historic_resample_buffer.tif'
# with rasterio.open(output_path, 'w', **R) as dst:
#     dst.write(bio_resample.astype(np.float32), 1)

# The area weighted value of biodiversity was calculated
area_weight = area * bio_resample

# The mean of each species for each land class is calculated
species_average = []
for land_class in range(6):  # 0:农田, 1:森林, 2:草地, 3:建设用地, 4:水体, 5:其他
    mask = (landuse1990 == land_class)
    if np.any(mask):
        species_average.append(np.nanmean(area_weight[mask]))
    else:
        species_average.append(np.nan)

print("Species average for each land class:", species_average)
