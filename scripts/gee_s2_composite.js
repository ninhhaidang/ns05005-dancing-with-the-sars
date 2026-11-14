// Chạy trong Google Earth Engine Code Editor (https://code.earthengine.google.com).
// Gộp (median) mọi cảnh Sentinel-2 SR trong 22/10-3/11/2026 thành một ảnh 10 m không mây cho AOI.
// Phản xạ = DN * 1e-4 (S2_SR_HARMONIZED đã hiệu chỉnh offset, không trừ thêm).

var aoi = ee.Geometry.Rectangle([105.8935, 20.249, 106.6595, 21.007]);   // khung bao Hưng Yên mới
var start = '2026-10-22', end = '2026-11-04';                              // 22/10 đến hết 3/11
var CS_THRESHOLD = 0.6;                                                    // Cloud Score+: càng cao càng nghiêm ngặt

var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(aoi).filterDate(start, end);
var csp = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED');
var clear = s2.linkCollection(csp, ['cs_cdf'])
  .map(function (i) { return i.updateMask(i.select('cs_cdf').gte(CS_THRESHOLD)); });

var bands = ['B2', 'B3', 'B4', 'B8', 'B11'];                               // blue, green, red, nir, swir16
var median = clear.select(bands).median().toInt16().clip(aoi);
var nClear = clear.select('B4').count().toInt16().rename('n_clear');       // số lần quan sát sạch mỗi pixel
var image = median.addBands(nClear);

print('Số cảnh', s2.size());
Map.centerObject(aoi, 9);
Map.addLayer(median, {bands: ['B4', 'B3', 'B2'], min: 0, max: 1500}, 'Màu thật (median)');
Map.addLayer(median, {bands: ['B8', 'B4', 'B3'], min: 0, max: 4000}, 'Màu giả NIR-R-G', false);
Map.addLayer(nClear, {min: 0, max: 6, palette: ['white', 'orange', 'green']}, 'Số lần sạch', false);

Export.image.toDrive({
  image: image,
  description: 'S2_composite_10m_20261022_20261103',
  folder: 'GEE_export',
  region: aoi,
  scale: 10,
  crs: 'EPSG:32648',            // trùng hệ tọa độ SAR (UTM 48N)
  maxPixels: 1e10,
  fileFormat: 'GeoTIFF',
  formatOptions: {cloudOptimized: true}
});
