import osmnx as ox
import re
import math
import fileinput

def get_sum_length_lanes(G):
  sum_length=0
  for (u,v,d) in G.edges(data=True):
#    print (d)
    if (isinstance(d['lanes'],list)):
       #regular expression is necessary cause there are errors in lanes attributes
       list_floats=list(map(lambda x: float(re.findall("^\s*\d+(?:\.\d+)?",x)[0]),d['lanes']))
#       print (list_floats)
       l=sum(list_floats)
    else:
       #; inside string to split count of different lanes, I think
       l=sum(map(lambda x: float(x),d['lanes'].split(';')))
    sum_length+=l*d['length']
  return sum_length

def get_stat_by_city (place):
  #search Polygon or MultiPolygon in OSM Nominative
  i=0
  while True:
    i=i+1
    gdf = ox.gdf_from_place(place,which_result=i)
#    print (i,':',gdf.type)
    if ((gdf.type[0]=='Polygon')or(gdf.type[0]=='MultiPolygon')):
      break
#  print ("Getting ",place,' #',i)
  area = ox.project_gdf(gdf).unary_union.area

  filtr='["lanes"!="1"]["oneway"="yes"]'
  filtr2='["lanes"!="2"]["lanes"!="1"]["oneway"!="yes"]'

  #retain_all=True cause our graph may be not connected
  G = ox.graph_from_place(place, which_result=i,retain_all=True,network_type='drive',custom_filter=filtr,infrastructure='way["lanes"]')
  G2 = ox.graph_from_place(place, which_result=i, retain_all=True,network_type='drive',custom_filter=filtr2,infrastructure='way["lanes"]')

  len = get_sum_length_lanes(G)
  len2 = get_sum_length_lanes(G2)
  result = ((len+len2),area,(len+len2)/math.sqrt(area))
  return result



ox.config(use_cache=True,log_file=True)
for line in fileinput.input():
    line = line.rstrip()
    (len,area,quality) = get_stat_by_city(line)
    print (line,';',len,';',area,';',quality)
    
    



