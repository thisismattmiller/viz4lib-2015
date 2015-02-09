#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os,json,glob,csv
from lxml import etree


class XMLFieldExtract(object):

	def __init__(self,resource):

		#the filename or the directory
		self.resource = resource


		self.elementUsePerFile = {}
		self.elementUsePerFileFlag = {}

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
				self.resetElementUsePerFileFlag()


		#or file
		elif os.path.isfile(resource):
			self.processFile(resource)
		else:
			print("Error: Could not locate that file or directory.")


		#the d3 viz just wants an list of the values so turn the dictonary into a list on output
		#so make it into a list


		elementUsePerFileList = []
		for x in self.elementUsePerFile:
			elementUsePerFileList.append(self.elementUsePerFile[x])



		with open("../data/xml_field_per_file_count.json","w") as w:
			w.write(json.dumps(elementUsePerFileList,indent=4))




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



		#dont do anything with empty elements if we dont want to
		if (el.text is  None or  el.text.strip() == "") and self.countEmptyNodes == False:
			return


		#store the basic count per file, so we need to check if we incremented it for this file or not
		if tag not in self.elementUsePerFileFlag:
			self.elementUsePerFileFlag[tag] = False


		#we have not yet set this file for having this element
		if self.elementUsePerFileFlag[tag] == False:
			if tag not in self.elementUsePerFile:
				self.elementUsePerFile[tag] = {"tag" : tag, "count": 1}
			else:
				self.elementUsePerFile[tag]['count']+=1			

			#don't count this one again for this file
			self.elementUsePerFileFlag[tag] = True


		


	def deNamespace(self,el):

		#cut the namespace off the tag name if it has it	
		if el.tag.find("}")>-1:
			tag = el.tag.split("}")[1]
		else:
			tag = el.tag		

		return tag


	#if we are count elements per file we use this to keep track when we tick one off for a file, so we need reset it after each file
	def resetElementUsePerFileFlag(self):
		for x in self.elementUsePerFileFlag:
			self.elementUsePerFileFlag[x] = False






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







