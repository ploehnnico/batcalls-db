import argparse
import batcalls_db
import config

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
	cfg = config.get_config()

	pass

if __name__ == "__main__":
	main()