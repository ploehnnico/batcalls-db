from batdb_class import BatcallsDB
import yaml
from matplotlib import pyplot as plt

def read_config(config_path):
	with open(config_path, 'r') as stream:
		config = yaml.safe_load(stream)
	return config


if __name__ == "__main__":
	config = read_config('config.yaml')
	# set up params
	# TODO: order csv file	
	dbfile = config['dbfile']
	callsfolder = config['newcalls']['folder']
	dbname = config['newcalls']['dbname']
	skip = config['newcalls']['skipif']
	description_csv = config['newcalls']['description']
	pos_offset = config['analysis']['pos_offset']
	neg_offset = config['analysis']['neg_offset']
	len_analysis = config['analysis']['len_analysis']

	# set up database
	batcallsdb = BatcallsDB(dbfile)
	# add calls
	batcallsdb.add_calls(callsfolder, dbname, description_csv,
						pos_offset, neg_offset, len_analysis, skip)