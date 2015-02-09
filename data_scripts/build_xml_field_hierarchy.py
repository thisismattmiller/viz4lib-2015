#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os,json,glob,csv
from lxml import etree


class XMLFieldExtract(object):

	def __init__(self,resource):

		#the filename or the directory
		self.resource = resource

		#we store the data in theses
		self.elementHierarchy = {}


		#count empty elements (no text)?
		self.countEmptyNodes = False


		#are we working with a dir
		if os.path.isdir(resource):

			#check for trailing slash
			if resource[len(resource)-1] != "/":
				resource+="/"

			#send each xml to the processor
			for fname in glob.glob(resource + "*.xml"):
				self.processFile(fname)


		#or file
		elif os.path.isfile(resource):
			self.processFile(resource)
		else:
			print("Error: Could not locate that file or directory.")


		#the sunburst file needs a csv file, so build that 
		csvRows = []
		for x in self.elementHierarchy:
			csvRows.append([self.elementHierarchy[x]['path'],self.elementHierarchy[x]['count']])

		with open('../data/xml_field_hierarchy_count.csv', 'w') as w:
			a = csv.writer(w, delimiter=',')			
			a.writerows(csvRows)



	#process the xml of a file, parse it and loop through the elements
	def processFile(self,file):

		#load the xml and parse
		print(file)
		with open(file,"r") as f:

			try:
				xml = f.read()
				root = etree.XML(xml)
			except Exception as e:
				print ("------------------")
				print("Error: Load and/or parse this file:")
				print(file)
				print("Error:")
				print(e)
				print ("------------------")
				return False


		for el in root.iter():
			if el != root:
				self.processElement(el,root)




	def processElement(self,el,root):

		tag = self.deNamespace(el)

		hierarchy = []
		parent = el.getparent()


		#if it is not a first child and it does not have cildren (el.iter() always returns itself, so 1 == no cildren)
		#then we want to store this hierarchial path
		if parent != root and len(list(el.iter())) == 1:
			
			#loop back up through the parents storing the names
			while parent != root:
				hierarchy.insert(0, self.deNamespace(parent))
				parent = parent.getparent()

			#add the current level at the end
			hierarchy.append(tag)

			#make the string path so it looks something like: "originInfo-place-placeTerm"
			path = "-".join(hierarchy)

			#record it
			if path not in self.elementHierarchy:
				self.elementHierarchy[path] = {"path" : path, "count": 1}
			else:
				self.elementHierarchy[path]['count']+=1



		#dont do anything with empty elements if we dont want to
		if (el.text is  None or  el.text.strip() == "") and self.countEmptyNodes == False:
			return


		


	def deNamespace(self,el):

		try:
			#cut the namespace off the tag name if it has it	
			if el.tag.find("}")>-1:
				tag = el.tag.split("}")[1]
			else:
				tag = el.tag		

			return tag

		except:
			return "?"

		




if __name__ == "__main__":


	if len(sys.argv) > 1:
		resource = sys.argv[1]
		m = XMLFieldExtract(resource)

	else:

		print ("------------------")
		print ("To use this script from the command line pass the filename or directory path as the first arugment.")
		print ("Example:")
		print ("python build_xml_field_list.py /Users/nypl/Desktop/xml")
		print ("------------------")







