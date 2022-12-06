import time
import json
import random
import base64
import requests
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import shape
from fake_useragent import UserAgent


class tiandituSpider(object):
    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-GB;q=0.6',
            'Connection': 'close',
            'Host': 'beijing.tianditu.gov.cn',
            'Origin': 'https://beijing.tianditu.gov.cn',
            'Referer': 'https://beijing.tianditu.gov.cn/bjtdt-main/electronicindex.html',
            'User-Agent': UserAgent().random,
        }

    def postTianditu(self, url: str, **kwargs) -> str:
        return requests.post(url, headers=self.headers, **kwargs).json()

    def decrypt(self, code: str) -> list:
        decoded = base64.b64decode(code).decode('utf-8')
        return json.loads(decoded)

    def encrypt(self, code: str) -> bytes:
        return base64.b64encode(code.encode('utf-8'))

    def swap_xy(self, MultiPolygon: list) -> list:
        for polygon in MultiPolygon:
            for line in polygon:
                for point in line:
                    point[0], point[1] = point[1], point[0]
        return MultiPolygon

    def queryAdminDistrict(self) -> dict:
        """
        Enquire name and gbcode for every district of Beijing,
        before passing gbcode to enquire geometry of each district.
        """
        url = 'https://beijing.tianditu.gov.cn/tianditu_pro/region/queryRegion'
        response = self.postTianditu(url)
        admin_division = self.decrypt(response.get('data'))
        names, geometries = [], []
        for district in tqdm(admin_division):
            name = district.get('name')
            gbcode = district.get('gbcode')
            geometry = self.queryGeometry(gbcode)
            names.append(name)
            geometries.append(geometry)
            time.sleep(random.uniform(1, 2))
        return {'name': names, 'geometry': geometries}

    def queryGeometry(self, gbcode: int):
        url = 'https://beijing.tianditu.gov.cn/tianditu_pro/region/queryRegionDetails'
        param = self.encrypt(f'{{"gbcode":"{gbcode}"}}')
        response = self.postTianditu(url, data=param)
        geomPolygon = self.decrypt(response.get('data')).get('geomPolygon')
        geomPolygon = self.swap_xy(json.loads(geomPolygon))
        geometry = shape({'type': 'MultiPolygon',
                          'coordinates': geomPolygon})
        return geometry

    @classmethod
    def start(cls):
        spider = cls()
        gdf = gpd.GeoDataFrame(spider.queryAdminDistrict(), crs='epsg:4326')
        gdf.to_file('Data/BeijingDistricts.shp', encoding='utf-8')


if __name__ == '__main__':
    tiandituSpider.start()
