from shapely import shape, intersects, intersection
import fiona

blockGroupShpFile = 'path/to/blockGroups.shp'
isdShpFile = 'path/to/ISD.shp'
isdWithCensusData = 'path/to/ISD_and_Data.shp'

with fiona.open(isdShpFile, 'r') as isds:
	
	#define a new schema from the isd shp file schema that includes a 'population' property
	newSchema = isds.schema
	newSchema['properties']['population']='float'

	#create new shp file for the isd records with additional census data properties
	with fiona.open( isdWithCensusData, 'w', driver = isds.driver, source = isds.schema, schema = newSchema) as isdPlus:

		with fiona.open(blockGroupShpFile, 'r') as bgs:
			for isd in isds:
				shapeISD = shape(isd['geometry'])
				isdPopulation = 0
				for bg in bgs:
					if shape(bg['geometry']).intersects( shapeISD ) == True:
						#compute area intersection of block group with the isd	
						shapeBG = shape( bg['geometry'] )
						areaBG = shapeBG.area
						areaIntersect = (shapeBG.intersection(shapeISD)).area
						percentArea = areaIntersect / areaBG
						#use that area intersection percentage and add the normalized amount of population to the ISD's total population
						#note: need to make sure block group file has a population feature which can be accessed as shown in the next line
						isdPopulation += percentArea * bg['population']

				#add the population count to the current record's properties and write the record to the isdWithCensusData shp file	
				isd['properties']['population'] = isdPopulation
				isdPlus.write(isd)