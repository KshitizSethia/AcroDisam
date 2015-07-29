import csv
import matplotlib.pyplot as plt

data = {}
with open("sw_train_abstracts.txt", "r") as file:
	reader = csv.reader(file, delimiter=",")
	for line in reader:
		acronym = line[1]
		expansion = line[-1]
		if( not acronym in data):
			data[acronym] = []
		if(not expansion in data[acronym]):
			data[acronym].append(expansion)
	
print "number of acronyms", len(data.keys())
	
numAmbs = []
for key in data.keys():
	num = len(data[key])-1
	if(num>0):
		numAmbs.append(num)

print len(numAmbs)
print max(numAmbs)

plt.subplot(121)
plt.title("Histogram of number of ambiguities")
plt.grid()
plt.yticks(range(1,66))
plt.hist(numAmbs)

plt.subplot(122)
plt.title("Plot of number of ambiguities")
plt.plot(numAmbs)

plt.show()