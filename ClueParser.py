#!/usr/bin/env python
# CS124 Homework 5 Jeopardy
# Original written in Java by Sam Bowman (sbowman@stanford.edu)
# Ported to Python by Milind Ganjoo (mganjoo@stanford.edu)

import sys
import itertools as it
from NaiveBayes import NaiveBayes
import re

class ClueParser:
    def __init__(self):
        # TODO: if your implementation requires one or more trained classifiers (it probably does), you should declare it/them here.
        # Remember to import the class at the top of the file (from NaiveBayes import NaiveBayes)
        # e.g. self.classifier = NaiveBayes()
        self.classifier = NaiveBayes()

    def feature_extractor(self, clue):
        """Given a clue represented as a raw string of text, extract features of the clue and return them as a list or set."""
        # NOTE: this function isn't called by the evaluation script, so feel free to use it or not however you want.
        
        features = []
        # Example: add the length of the clue to the features (it's not very effective...)
        keyWords = ["spouse", "married", "wife", "husband", "college", "university in", "president of", "headquarters in", \
        "headquartered in", "born in", "parent organization", "parent company of", "mayor of", "university in", "born", "died"]
        for word in re.split(' ', clue):
            if word not in ["the", "of", "a", "an", "but", "then", "to", "I", "you", ".", "?"]:
                if len(word) > 1 and (word[len(word)-1] == "?" or word[len(word)-1] == "." or word[len(word)-1] == ","):
                    features.append(word[:-1])
                else:
                    features.append(word)
        for word in keyWords:
            if word in clue.split():
                features.append(word)

        # TODO Add more features!
        return features

    def train(self, clues, parsed_clues):
        """Trains the model on clues paired with gold standard parses."""
        # TODO: If your implementation of ClueParser uses any classifiers (it probably does), train them here
        klasses = ["wife_of", "husband_of", "college_of", "univ_president_of", "headquarters_loc", "born_in", "parent_org_of", "mayor_of", "univ_in", "year_of_birth", "year_of_death"]
        labels = []
        features_list = []
        for i in xrange(len(clues)):
            label = parsed_clues[i].split(":")[0]
            labels.append(label)
            self.classifier.addExample(label, self.feature_extractor(clues[i]))
            features_list.append(self.feature_extractor(clues[i]))
        
#        self.classifier.crossValidate(features_list, labels)

    def parseClues(self, clues):
        """Parse each clue and return a list of parses, one for each clue."""
        parses = []
        for clue in clues:
            # TODO extract the clue relation and entity and append them to the list of parses
            clue_relation = self.classifier.classify(self.feature_extractor(clue))
            if clue_relation == "mayor_of" or clue_relation == "univ_in":                 
                entity = '<LOCATION>(.*?)</LOCATION>'
                keyWords = re.findall(entity, clue, flags=re.IGNORECASE)
                if len(keyWords) > 1:          
                    clue_entity = keyWords[0] + ", " + keyWords[1]
                elif len(keyWords) == 1:
                    entity = '<LOCATION>(.*?)</LOCATION>, ([A-Z][A-Z])'
                    keyWords = re.findall(entity, clue, flags=re.IGNORECASE)
                    if len(keyWords) > 0:
                        clue_entity = keyWords[0][0] + ", " + keyWords[0][1]
                    else:
                        entity = '(.*?)'
                        clue_entity = re.findall(entity, clue, flags=re.IGNORECASE)[0]
                else:
                    entity = '(.*?)'
                    clue_entity = re.findall(entity, clue, flags=re.IGNORECASE)[0]

            elif clue_relation in ["univ_president_of", "parent_org_of"]:
                entity = '<ORGANIZATION>(.*?)</ORGANIZATION>'
                keyWords = re.findall(entity, clue, flags=re.IGNORECASE)
                if len(keyWords) > 0:
                    clue_entity = keyWords[0]
                else:
                    entity = '([A-Z].*?)'
                    clue_entity = re.findall(entity, clue, flags=re.IGNORECASE)[0]


            elif clue_relation in ["wife_of", "husband_of", "college_of", "born_in", "year_of_birth", "year_of_death"]:
                entity = '<PERSON>(.*?)</PERSON>'
                keyWords = re.findall(entity, clue, flags=re.IGNORECASE)
                if len(keyWords) > 0:
                    clue_entity = keyWords[0]
                else:
                    entity = '([A-Z].*?)'
                    clue_entity = re.findall(entity, clue, flags=re.IGNORECASE)[0]
            else:
                entity = '>([A-Z].*?)<'
                keyWords = re.findall(entity, clue, flags=re.IGNORECASE)
                if len(keyWords) != 0:
                    clue_entity = keyWords[0]
                else:
                    entity = '(.*?)'
                    clue_entity = re.findall(entity, clue, flags=re.IGNORECASE)[0]

            parses.append(clue_relation + ':' + clue_entity)
        return parses

    #### You should not need to change anything after this point. ####

    def evaluate(self, parsed_clues, gold_parsed_clues):
        """Shows how the ClueParser model will score on the training/development data."""
        correct_relations = 0
        correct_parses = 0
        for parsed_clue, gold_parsed_clue in it.izip(parsed_clues, gold_parsed_clues):
            split_parsed_clue = parsed_clue.split(":")
            split_gold_parsed_clue = gold_parsed_clue.split(":")
            # if parsed_clue != gold_parsed_clue:
            #     print split_parsed_clue
            #     print split_gold_parsed_clue
            if split_parsed_clue[0] == split_gold_parsed_clue[0]:
                correct_relations += 1
                if (split_parsed_clue[1] == split_gold_parsed_clue[1] or
                        split_parsed_clue[1] == "The " + split_gold_parsed_clue[1] or
                        split_parsed_clue[1] == "the " + split_gold_parsed_clue[1]):
                    correct_parses += 1
        print "Correct Relations: %d/%d" % (correct_relations, len(gold_parsed_clues))
        print "Correct Full Parses: %d/%d" % (correct_parses, len(gold_parsed_clues))
        print "Total Score: %d/%d" % (correct_relations + correct_parses, 2 * len(gold_parsed_clues))

def loadList(file_name):
    """Loads text files as lists of lines. Used in evaluation."""
    with open(file_name) as f:
        l = [line.strip() for line in f]
    return l

def main():
    """Tests the model on the command line. This won't be called in
        scoring, so if you change anything here it should only be code 
        that you use in testing the behavior of the model."""

    clues_file = "data/part1-clues.txt"
    parsed_clues_file = "data/part1-parsedclues.txt"
    cp = ClueParser()

    clues = loadList(clues_file)
    gold_parsed_clues = loadList(parsed_clues_file)
    assert(len(clues) == len(gold_parsed_clues))

    cp.train(clues, gold_parsed_clues)
    parsed_clues = cp.parseClues(clues)
    cp.evaluate(parsed_clues, gold_parsed_clues)
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        print "\nValidation results:"
        clues_file = "data/part2-clues-val.txt"
        parsed_clues_file = "data/part2-parses-val.txt"
        
        clues = loadList(clues_file)
        gold_parsed_clues = loadList(parsed_clues_file)
        assert(len(clues) == len(gold_parsed_clues))
        
        parsed_clues = cp.parseClues(clues)
        cp.evaluate(parsed_clues, gold_parsed_clues)

if __name__ == '__main__':
    main()
