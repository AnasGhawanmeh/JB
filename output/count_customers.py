import sys, geopandas as gpd
zp, sp, out = sys.argv[1:4]
z = gpd.read_file(zp); s = gpd.read_file(sp).to_crs(z.crs)
j = gpd.sjoin(s[['geometry']], z[['geometry']], predicate='intersects', how='inner')
z['Cust_Count'] = j.groupby('index_right').size().reindex(z.index, fill_value=0).astype('int64')
z.to_file(out, encoding='UTF-8')
print('total in zones', z.Cust_Count.sum(), 'unique', j.index.nunique(), 'outside', len(s)-j.index.nunique())
print(z.drop(columns='geometry').sort_values('Cust_Count',ascending=False).head(10)[['id','Name','Sub_zone_N','Cust_Count']])
print(z[z.Cust_Count==0][['id','Name','Sub_zone_N']])
