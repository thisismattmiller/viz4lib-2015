#!/usr/bin/env python
# -*- coding: utf-8 -*-


import string, os, sys, json, unicodedata
import xml.etree.ElementTree as etree
from bs4 import BeautifulSoup


class subjectNetwork:


	dataPath = 'path/to/xml/files/'


	extention = '.xml'
	xmlFiles = []
	exclude = set(string.punctuation)

	#EAD and MODS controled terms
	elements = ['persname','corpname','subject','topic']

	#change these to larger numbers to make the graph smaller (less complex, less nodes and edges)

	#a connection between two subjects must have at least edgeWeightLimit connections
	edgeWeightLimit = 2
	#a subject heading must have appeared subjectCountLimit number of times for it to be included
	subjectCountLimit = 10



	globalSubjects = {}
	globalSubjectsCount = 0


	globalSubjectsRelationships = {}
	globalSubjectsRelationshipsCount = 0


	globalTotalRecords = 0


	


	def __init__(self):

		self.getFileNames()

		for a in self.xmlFiles:

			self.processFile(a)



		self.buildGraph()

		

		print ""
		print "Total Subjects:", "{:,}".format(self.globalSubjectsCount)
		print "Total Records:", "{:,}".format(self.globalTotalRecords)
		print "Total Subject Relationships:", "{:,}".format(self.globalSubjectsRelationshipsCount)

	def getFileNames(self):
		for file in os.listdir(self.dataPath):
			if file.endswith(self.extention):
				self.xmlFiles.append(self.dataPath + file)

	def normalizeSubject(self, subject):

		org = subject

		#no punctuations
		subject = ''.join(ch for ch in subject if ch not in self.exclude)

		#no spaces
		subject = "".join(subject.split())

		#no case
		subject = subject.lower()

		#so....all punctuation subject heading...
		if subject=='':
			subject = '???'

		#try for no diacritics
		try:

			subject = unicodedata.normalize('NFKD', subject).encode('ascii','ignore')

		except:

			subject = subject
			

		return subject


	def processFile(self, file):

		print ""

		print "Total Subjects:", "{:,}".format(self.globalSubjectsCount)
		print "Total Records:", "{:,}".format(self.globalTotalRecords)

		print "Processing next file:"
		print file

		count = 0
		self.globalTotalRecords+=1

		subjects = []





		with open (file, "r") as xmlFile:

			xmlData=xmlFile.read()
			soup = BeautifulSoup(xmlData,features="xml")

			for lookFor in self.elements:

				elements = soup.findAll(lookFor)

				for element in elements:
					

					if element.text.strip() != "":


						if element.text not in subjects:

							subjects.append(element.text)


		if len(subjects) != 0:


			subjectsNormalized = []

			for s in subjects:

				normalized = self.normalizeSubject(s)

				subjectsNormalized.append(normalized)

				if normalized not in self.globalSubjects:

					self.globalSubjects[normalized] = {  "subject" : s, "count" : 1, "id" : self.globalSubjectsCount, "added" : False}
					
					self.globalSubjectsCount+=1

		
				else:

					self.globalSubjects[normalized]['count']+=1


			#now make the relationships 
			for ns in subjectsNormalized:
				for ns2 in subjectsNormalized:
					if ns != ns2:

						#not ourselfs see if this relationships is defined yet

						mushedId = ns + ns2
						mushedIdReverse = ns2 + ns

						if mushedId not in self.globalSubjectsRelationships and mushedIdReverse not in self.globalSubjectsRelationships:

							self.globalSubjectsRelationships[mushedId] = { "id" : self.globalSubjectsRelationshipsCount,  "term1" : ns, "term1Id" : self.globalSubjects[ns]['id'], "term2" : ns2, "term2Id" : self.globalSubjects[ns2]['id'], "weight" : 1}								

							self.globalSubjectsRelationshipsCount+=1

						else:


							if mushedId in self.globalSubjectsRelationships:
								self.globalSubjectsRelationships[mushedId]['weight']+=1
							else:
								self.globalSubjectsRelationships[mushedIdReverse]['weight']+=1
					



	def buildGraph(self):


		subjectByCount = sorted(self.globalSubjects,key=lambda x:self.globalSubjects[x]['count'], reverse=True)

		header = '<?xml version="1.0" encoding="UTF-8"?>'

		gexf = etree.Element('gexf', xmlns='http://www.gexf.net/1.2draft', version='1.2')

		graph = etree.Element('graph', mode='static', defaultedgetype='undirected')

		nodes = etree.Element('nodes')

		edges = etree.Element('edges')

		addedNodes = []

		print (subjectByCount)

		for x in subjectByCount:

			if (self.globalSubjects[x]['count'] > self.subjectCountLimit):
				nodes.append(etree.Element('node', id=str(self.globalSubjects[x]['id']), label=self.globalSubjects[x]['subject'], weight=str(self.globalSubjects[x]['count'])))
				self.globalSubjects[x]['added'] = True
				addedNodes.append(x)

		graph.append(nodes)



		edgesAdded = {}



		count = 0
		countTotal = 0
		reportCount = 0

		for x in self.globalSubjectsRelationships:

			count+=1

			if (count > 5000):
				countTotal = countTotal + count
				count = 0
				sys.stdout.write("\rBuilding Relationships: %d%% done." %round(countTotal / len(self.globalSubjectsRelationships) * 100, 1))

			edge = self.globalSubjectsRelationships[x]


			if edge['weight']  < self.edgeWeightLimit:
				continue

			

			

			#make sure both subjects invoved had enough # of records to make the cut


			if self.globalSubjects[edge['term1']]['added'] == True and self.globalSubjects[edge['term2']]['added'] == True:


				term1 = edge['term1'] + edge['term2']
				term2 = edge['term2'] + edge['term1']

				if (term1 not in edgesAdded and term2 not in edgesAdded):

					edgesAdded[term1] = True
					edgesAdded[term2] = True

					edges.append(etree.Element('edge', id=str(edge['id']), weight=str(edge['weight']), source=str(edge['term1Id']), target=str(edge['term2Id'])))
					reportCount+=1

			





		print "\n\nGEXF stats:"
		print "Node count:", "{:,}".format(len(addedNodes))
		print "Edge count:", "{:,}".format(reportCount)


		graph.append(edges)


		gexf.append(graph)
		

		s = etree.tostring(gexf, 'utf-8')
		
		gefxFile = open("../data/xml_output.gexf", "w")
		gefxFile.write(header)
		gefxFile.close()


		gefxFile = open("../data/xml_output.gexf", "ab")
		gefxFile.write(s)
		gefxFile.close()






if __name__ == "__main__":

	s = subjectNetwork()
