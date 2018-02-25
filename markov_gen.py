import markovify
import pickle
import pronouncing as p
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str, help="The name of the input text")

class RapIndex:
    def __init__(self):
        self.rhymeIndex = dict()
        self.markovIndex = dict()


    def addMarkov(self, key, value):
        if key in self.markovIndex:
            if value in self.markovIndex[key]:
                self.markovIndex[key][value] += 1
            else:
                self.markovIndex[key][value] = 1
        else:
            entry = dict()
            entry[value] = 1
            self.markovIndex[key] = entry
    
    def addRhyme(self, word):
        if len(word) == 1 and word not in 'ia':
            return

        phones = p.phones_for_word(word)
        if len(phones) != 0:
            phones = phones[0].split(" ")
            i = len(phones) - 1
            stub = ""
            while i >= 0:
                if any(char.isdigit() for char in phones[i]):
                    if (stub+phones[i]) in self.rhymeIndex:
                        self.rhymeIndex[stub+phones[i]].add(word)
                    else:
                        self.rhymeIndex[stub+phones[i]] = set([word])
                    break
                stub += phones[i]
                i -= 1

    def markovNext(self, word):
        if word not in self.markovIndex:
            raise RuntimeError
        choices = []
        for key in self.markovIndex[word]:
            for i in range(self.markovIndex[word][key]):
                choices.append(key)
        return random.choice(choices)

    def getRhymingWords(self, num=2):
        vowels = [key for key in self.rhymeIndex]
        while len(vowels) > 0:
            choice = random.choice(vowels)
            if len(self.rhymeIndex[choice]) < num:
                vowels.remove(choice)
            else:
                words = [word for word in self.rhymeIndex[choice]]
                returnList = []
                while len(returnList) < num:
                    wordChoice = random.choice(words)
                    returnList.append(wordChoice)
                    words.remove(wordChoice)
                return returnList
        return None
    
    def getBars(self, numBars=2, exp_length=6):
        endWords = self.getRhymingWords(num=numBars)

        bars = []
        for word in endWords:
           current_line = word
           current_word = word
           while current_word != '--':
               current_word = self.markovNext(current_word)
               if current_word != '--':
                   current_line = current_word + " " + current_line
           bars.append(current_line) 
        return bars


        
    def save(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        with open(filename, "rb") as f:
            dump = pickle.load(f)
            self.markovIndex = dump.markovIndex
            self.rhymeIndex = dump.rhymeIndex


if __name__ == "__main__":
    args = parser.parse_args()
    
    index = RapIndex()

    print("Building rap index!")
    with open(args.input_file, "r") as f:
        for line in f:
            if line.strip() != "":
                words = line.split(" ")
                i = len(words) - 1
                if i > 0:
                    index.addRhyme(words[i].strip())
                while i > 0:
                    index.addMarkov(words[i].strip(), words[i-1].strip())
                    i -= 1
                index.addMarkov(words[i].strip(), "--")
    print(index.getBars())
