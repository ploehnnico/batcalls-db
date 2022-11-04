import sqlite3
import logging
import numpy as np
import os
from batcalls_db import tools
from batcalls_db import processing
import multiprocessing as mp
import sys
import warnings
from functools import partial

class BatcallsDB:

	def __init__(self, dbpath):
		self.dbpath = dbpath 
		self.rows = []
		self.hashes = []
		self.species = dict()
		self.targets = dict()
		self.callcounter = 0
		sqlite3.register_adapter(np.ndarray, tools.adapt_array)
		sqlite3.register_converter("array", tools.convert_array)
		self.check_existing_db()


	def create_new_db(self, dbpath):
		schema = ('call INTEGER, target INTEGER, id INTEGER, bat TEXT,'
				  'arr ARRAY, db TEXT, file TEXT, filepart INTEGER, calltype TEXT')
		with sqlite3.connect(dbpath, 
							 detect_types=sqlite3.PARSE_DECLTYPES) as con:
			cur = con.cursor()
			cur.execute("create table batcalls (%s)" %schema)
		pass
	
	def add_rows_to_db(self, rows):
		dbpath = self.dbpath
		with sqlite3.connect(dbpath, 
							 detect_types=sqlite3.PARSE_DECLTYPES) as con:
			cur = con.cursor()
			table_list = [a for a in cur.execute("""SELECT name FROM
						  sqlite_master WHERE type = 'table'""")]
			table = table_list[0][0]	
			cur.executemany("""insert into %s values (?, ?, ?, ?, ?, ?, ?,
							?, ?)""" %table, rows)

	def delete_rows_from_table(self, **kwargs):
		pass

	def check_existing_db(self):
		dbpath = self.dbpath
		with sqlite3.connect(dbpath) as con:
			cur = con.cursor()
			table_list = [a for a in cur.execute("""SELECT name FROM
						  sqlite_master WHERE type = 'table'""")]
			if not table_list:
				logging.info('No existing DB found. Creating new one.')
				self.create_new_db(dbpath)
				return
			else:
				table = table_list[0][0]
			query = ("SELECT call, target, bat, db, file, filepart "
					"FROM '%s'") %table
			rows = [a for a in cur.execute(query)]
			logging.info('Found existing DB with table: %s and %s rows'
						 %(table, str(len(rows))))
		self.callcounter = len(rows)
		allhashes = [row[4] for row in rows]
		self.hashes = np.unique(allhashes)
		allspecies = [row[2] for row in rows]
		species = np.unique(allspecies)
		self.species = {s : allspecies.count(s) for s in species}
		logging.info('Found %i different species in existing database' %(len(species)))
		logging.info('Found %i different soundfiles in existing database' %(len(self.hashes)))
		for s in species:
			for r in rows:
				if r[2] == s:
					self.targets[s] = r[1]
					break
		pass

	def count_call(self):
		c = self.callcounter
		self.callcounter += 1
		return c 
	
	def get_species_id(self, species):
		id = self.species[species]
		self.species[species] = id + 1
		return int(id)

	def process_file(self, cfg, filepath):
		_, filename = os.path.split(filepath)
		if not tools.iswavfile(filepath):
			logging.info('Not a .wav file. Skip processing. %s' %filepath)
			return None
		bat = self.file_to_species.get(filename, None)
		if not bat:
			logging.info('''No description for file %s! Skipping
						 processing...''' %filename)
			return None
		if bat == cfg.IMPORT.SKIP:
			logging.info('Skipping processing of file %s' %filename)
			return None
		# compute md5 hash
		hash = tools.md5hashfile(filepath)

		# if file is already in db dont process
		with warnings.catch_warnings():
			warnings.simplefilter(action='ignore', category=FutureWarning)
			if hash in self.hashes:
				logging.info('File already exists in database. Skip processing.')
				return None

		if cfg.PROCESSING.METHOD:
			calls = processing.process_without_cut(filepath, cfg)
		else:
			calls = processing.process_file(filepath, cfg)

		return filepath, calls

	def create_rows(self, calls, dbname):
		rows = []
		for filepath, arrs in calls:
			_, filename = os.path.split(filepath)
			bat = self.file_to_species[filename]
			calltype = self.file_to_call_type[filename]
			target = self.targets[bat]
			hash = tools.md5hashfile(filepath)
			for j, arr in enumerate(arrs):
				id = self.get_species_id(bat)
				call = self.count_call()	
				row = [call, target, id, bat, arr, dbname, hash, j, calltype]
				rows.append(row)
		return rows

	def parse_species_csv(self, path):
		if not os.path.isfile(path):
			raise ValueError('Provided file %s does not exist.' %path)
		_, ext = os.path.splitext(path)
		if ext != '.csv':
			raise ValueError('File %s is not a csv file. Valid file required.')
		with open(path, 'r') as stream:
			lines = stream.readlines()
		# fix format
		lines = [tools.removenewline(s).split(',')
				 for s in lines]
		file_to_species = {l[0].lower() : ''.join(l[1].split()).lower() for l in lines}
		file_to_calltype = {l[0].lower() : l[-1].lower()  for l in lines}
		return file_to_species, file_to_calltype

	def add_new_species(self, newspecies):
		self.species = {**self.species, **{s: 0 for s in newspecies}}
		maxtarget = 0 if not self.targets else max(self.targets.values())
		newtargets = {s: i + maxtarget for i, s in enumerate(newspecies)}
		self.targets = {**self.targets, **newtargets}
		pass

	def add_calls(self, cfg):
		file_to_species, file_to_calltype = self.parse_species_csv(cfg.IMPORT.CSVPATH)	
		self.file_to_species = file_to_species
		self.file_to_call_type = file_to_calltype
		allspecies = np.unique(list(file_to_species.values()))
		newspecies = [s for s in allspecies if s not in self.species]
		logging.info('Found %s new species: \n%s' 
					  %(len(newspecies), '\n'.join(newspecies)))
		b = input('Add new species to db? [y/n]') == 'y'
		if not b:
			logging.info('Stopping...')
			return
		self.add_new_species(newspecies)
		callspath = cfg.IMPORT.FOLDER
		files = [callspath + file.lower() for file in os.listdir(callspath)]
		n = 100 # write to db all n calls
		filelist = [files[i:i+n] for i in range(0, len(files), n)]
		for i, files in enumerate(filelist):
			logging.info('Starting run %i of %i.' %(i + 1, len(filelist)))
			cpus = mp.cpu_count()
			pool = mp.Pool(processes=cpus)
			process = partial(self.process_file, cfg)
			results = pool.map(process, files)
			pool.close()
			pool.join()
			failures = results.count(None)
			if failures:
				logging.info('%i files failed to process' %failures)
			results = [x for x in results if x is not None]
			if not results:
				continue
			rows = self.create_rows(results, cfg.IMPORT.NAME)
			logging.info('Done, wrtiting to database.')
			self.add_rows_to_db(rows)
		pass	