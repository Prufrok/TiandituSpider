# TiandituSpider
[天地图·北京（在线地图）](https://beijing.tianditu.gov.cn/bjtdt-main/electronicindex.html)上行政边界空间数据的简易爬虫，
部分参考[这篇博客](https://blog.csdn.net/weixin_45459224/article/details/123002406)

* 爬虫流程：post请求获取北京所有区的gbcode后再次post请求获取对应的geometry坐标点
* 将结果保存为wgs84地理坐标系的shp格式
* 如果要爬取北京市乡镇街道的地理数据流程类似
