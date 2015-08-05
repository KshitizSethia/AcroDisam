import csv
from string_constants import file_ScienceWise_index_train,\
    folder_scienceWise_pdfs
import urllib2
import time

from Logger import common_logger

def downloadPdfs():
    with open(file_ScienceWise_index_train, "r") as file:
        reader = csv.DictReader(file, delimiter=",")
        for line in reader:
            pdfID = line["ARXIV_ID"]
            pdfID = pdfID.replace("/", "_").replace("\\","_")
            try:
                _downloadPdf(pdfID)
                common_logger.debug("successfully downloaded " +pdfID)
                time.sleep(15*60)
            except:
                common_logger.exception("Error in file " +pdfID)
            
def _downloadPdf(pdfID):
    filename = pdfID +".pdf"
    url = "http://arxiv.org/pdf/" +filename
    response = urllib2.urlopen(url)
    local_file = open(folder_scienceWise_pdfs +filename, "wb")
    local_file.write(response.read())
    response.close()
    local_file.close()

def visualize():
    import matplotlib.pyplot as plt
    
    data = {}
    with open(file_ScienceWise_index_train, "r") as file:
        reader = csv.reader(file, delimiter=",")
        for line in reader:
            acronym = line[1]
            expansion = line[-1]
            if( not acronym in data):
                data[acronym] = []
            if(not expansion in data[acronym]):
                data[acronym].append(expansion)
        
    print("number of acronyms", len(data.keys()))
        
    numAmbs = []
    for key in data.keys():
        num = len(data[key])-1
        if(num>0):
            numAmbs.append(num)
    
    print(len(numAmbs))
    print(max(numAmbs))
    
    plt.subplot(121)
    plt.title("Histogram of number of ambiguities")
    plt.grid()
    plt.yticks(range(1,66))
    plt.hist(numAmbs)
    
    plt.subplot(122)
    plt.title("Plot of number of ambiguities")
    plt.plot(numAmbs)
    
    plt.show()
    
if __name__ == "__main__":
    downloadPdfs()