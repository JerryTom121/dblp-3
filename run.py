from lxml import etree
import networkx as nx

source = 'dblp.xml'
dtd = etree.DTD(file='dblp.dtd') #need to change second line in dblp.xml

author=[]
title=[]
G=nx.Graph()

for event, element in etree.iterparse(source, load_dtd=True):
    if 	element.getchildren() and element.tag!="dblp" and element.tag!="www":
        if len(author)>1:
            for person in author:
                if G.has_node(person):
                    temp = G.node[person]["title"] + title
                    G.add_node(person,title=temp)
                else:
                    G.add_node(person,title=title)
            for i in range(0,len(author)-1):
                for j in range(i+1,len(author)):
                    p1,p2=author[i],author[j]
                    if G.has_edge(p1,p2):
                        G[p1][p2]['weight']+=1
                    else:
                        G.add_edge(p1,p2,weight=1)
        elif len(author)==1:
            if G.has_node(author[0]):
                title = G.node[author[0]]["title"] + title
            G.add_node(author[0],title=title)
        author=[]
        title=[]
        continue
    if element.tag=="author" or element.tag=="editor":
        name = element.text.replace("\"","")
        if len(name.split())==1:
            name="\""+name+"\""
        author.append(name)
    if element.tag=="title" or element.tag=="booktitle" or element.tag=="journal":
        title.append(element.text.replace("\"","").replace("\'",""))

    element.clear()

# nx.write_pajek(G, "dblp.net")

lc = sorted(nx.connected_component_subgraphs(G), key = len, reverse=True)[0]
# nx.write_pajek(lc, "lc.net")

similar_names = {}
all_nodes = lc.nodes()
for node in all_nodes:
    if node[-4:].isdigit() and len(node)>4:
        name = node[:-5].strip()
        if name in all_nodes:
            if name in similar_names:
                similar_names[name][node] = graph.node[node]["id"]
            else:
                similar_names[name] = {name:graph.node[name]["id"],node:graph.node[node]["id"]}
count_list = (len(key) for key in similar_names.values())
top_10 = sorted(count_list,reverse=True)[9]
selection = [key for key,value in similar_names.items() if len(value) >= top_10]
print "number of similar names: ",len(similar_names.keys()) #1397
c = (len(key) for key in similar_names.values())
top = sorted(c,reverse=True)[:10]
s = [(key,len(value)) for key,value in similar_names.items() if len(value) in top]

for case in selection:
    graph = nx.ego_graph(lc,case)
    for pair in similar_names[case]:
        subgraph = nx.ego_graph(lc,pair)
        graph = nx.compose(graph,subgraph)
    nx.write_pajek(graph, str(case)+".net")
