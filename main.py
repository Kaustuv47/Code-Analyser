import os
import re
import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt

pattern = re.compile(r"p\w+->\w+")
structVariableGraph = nx.MultiDiGraph()
structVariableList = []
filePath = ""
# documentPath = Path(os.environ['USERPROFILE'], 'Documents')
documentPath = Path(os.environ['USERPROFILE'], 'Desktop')
documentPath = Path('.')

def GetCFiles(sourcePath):
    noCFilesAvailable = True
    for directory in sourcePath.iterdir():
        if directory.is_dir():
            filesList = list(directory.glob('**/*.c'))
            if filesList != []:
                noCFilesAvailable = False
                for file in filesList:
                    ReadFile(Path(file).absolute())
    if noCFilesAvailable:
        print("No C file found in directory")

def FindStructVariables(line):
    for eachStructVariable in pattern.findall(line):
        if eachStructVariable not in structVariableList:
            structVariableList.append(eachStructVariable)

def CreateSubStructVariableList():
    for index, eachStructVariable in enumerate(structVariableList):
        structVariableList[index] = [eachStructVariable.split('->')[0], eachStructVariable.split('->')[1]]

def CreateStructVariableGraph():
    for parent, child in structVariableList:
        if structVariableGraph.has_node(parent):
            if structVariableGraph.has_node(child):
                if not structVariableGraph.has_edge(parent, child):
                    structVariableGraph.add_edge(parent, child)
            else:
                structVariableGraph.add_node(child)
                structVariableGraph.add_edge(parent, child)
        else:
            structVariableGraph.add_node(parent)
            structVariableGraph.add_node(child)
            structVariableGraph.add_edge(parent, child)


def SaveStructureVariableGraph(outputPath, fileFormat = None):
    if fileFormat == 'Image':
        plt.title('Structure Variable')
        plt.figure(figsize=(200, 50))
        pos = nx.nx_agraph.graphviz_layout(structVariableGraph, prog="dot")
        nx.draw(structVariableGraph, pos, with_labels=True, arrows=True, node_size=1200)
        plt.savefig(Path(outputPath, 'StructVariableGraph.png'))
    else:
        nx.write_graphml(structVariableGraph, str(Path(outputPath, "StructVariableGraph.gz")), encoding='utf-8', prettyprint=True, infer_numeric_types=False, named_key_ids=False, edge_id_from_attribute=None)

def OpenStructureVariableGraph(filePath):
    global structVariableGraph
    structVariableGraph = nx.read_graphml(filePath, force_multigraph=True)

def KnowStructureVariableSource(variable, filePath = None):
    if filePath == None:
        OpenStructureVariableGraph(Path(documentPath, "StructVariableGraph.gz"))
    else:
        OpenStructureVariableGraph(Path(filePath, "StructVariableGraph.gz"))
    T = nx.dfs_tree(structVariableGraph.reverse(), source=variable).reverse()
    print(T)
    parentStructure = nx.ancestors(structVariableGraph, variable)
    if parentStructure != []:
        for parent in nx.ancestors(structVariableGraph, variable):
            print(parent, end=" -> ")
        print(variable)
        return True
    return False

def ReadFile(fileName):
    file = open(fileName, 'r', errors='ignore')
    for line in file.readlines():
        FindStructVariables(line)
    file.close()

if __name__ == "__main__":
    while True:
        if Path.exists(Path(documentPath, "StructVariableGraph.gz")):
            while True:
                variable = input("Variable ->  ")
                print("======================================")
                status = KnowStructureVariableSource(variable)
                print("======================================")
                if status == True:
                    pass
                elif variable == "K":
                    exit(1)
                else:
                    print("Enter Correct variable name")
        else:
            sourcePath = None
            while True:
                # C:\Workspace\drivers.gpu.unified.git
                sourcePath = Path(input("Enter Source path -> "))
                if Path.exists(sourcePath):
                    break
                elif str(sourcePath).upper() == "K":
                    exit(1)
                else:
                    print("Path not valid")
            GetCFiles(sourcePath)
            CreateSubStructVariableList()
            CreateStructVariableGraph()
            SaveStructureVariableGraph(documentPath)
            print("File Created")











