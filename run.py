import argparse
from batcalls_db.batdb_class import BatcallsDB
import config
import logging
import sys

def setup_logging():
	root = logging.getLogger()
	root.setLevel(logging.INFO)

	handler = logging.StreamHandler(sys.stdout)
	handler.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	root.addHandler(handler)

def parse_args():
	parser = argparse.ArgumentParser(
		description='Build batcalls database'
	)
	parser.add_argument('--cfg',
						help='config file path',
						type=str)
	args = parser.parse_args()
	return args


def main():
	setup_logging()
	cfg = config.get_cfg('./config/config.yaml')
	logging.info("Using config: \n%s" %cfg)
	batcalls_db = BatcallsDB(cfg.DBPATH)
	batcalls_db.add_calls(cfg)
	pass

if __name__ == "__main__":
	main()