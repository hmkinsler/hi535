# Network mapping script for racially restrictive covenants data
setwd("C:/Users/hmkinsle/Documents/vs_code/hi535/r")
rc <- read.csv("rcc_v1_data.csv")

library(igraph)
library(ggraph)
library(tidygraph)
library(dplyr)
library(reshape2)

# Ensure column names are lowercase
colnames(rc) <- tolower(colnames(rc))

# Create weighted edge list tracing grantor - grantee relationships
edges <- rc %>% 
  count(grantor, grantee) %>% 
  rename(weight = n) %>% 
  arrange(desc(weight))

View(edges)

grantor_count <- rc %>% count(grantor) %>% arrange(desc(n)) 

View(grantor_count) # a small number of grantors were responsible for many covenants

grantee_count <- rc %>% count(grantee) %>% arrange(desc(n)) # a small number of grantors were responsible for many covenants

View(grantee_count) # a minority of grantees had more than 3 covenants

# Only keep strongest network relationships and maintain direction of deed flows
edges <- edges %>% 
  filter(weight >= 5) #RD: I didn't do this step, for now, so that I could see the network based on the full dataset. It does get overwhelming, but I laid out a couple ideas below that might help.

#Create data frame saying which vertices are grantors and which are grantees:
grantor_count$role <- 'grantor'
grantee_count$role <- 'grantee'

#Deal with the fact that quite a few nodes were both grantors and grantees:
both <- grantor_count$grantor[grantor_count$grantor%in%grantee_count$grantee]
length(both) #1919

grantor_count$role[grantor_count$grantor%in%both] <- 'both'
#Check: 
table(grantor_count$role) #good

#Grantees not in both:
just_grantee <- grantee_count$grantee[!grantee_count$grantee%in%grantor_count$grantor]
length(just_grantee) #8454

just_grantees <- data.frame(grantor=just_grantee, role=rep('grantee', 8454))

#Make data frame with node names and roles:
cov_vertices <- data.frame(rbind(grantor_count[,-2], just_grantees))
head(cov_vertices)

names(cov_vertices) <- c('name', 'role')
#Check:
head(cov_vertices)

#This is the same function you used to make a graph object, but I added a value to the 'vertices' argument.
covnet <- graph_from_data_frame(edges, directed = TRUE, vertices=cov_vertices)

#Here's a graph that shows (somewhat) well the fact that there's a dense core plus a lot of peripheral, single- or dual-covenant nodes.
ggraph(covnet, layout = "fr") +  
  geom_edge_link(aes(edge_alpha = weight)) +
  geom_node_point(size = 2, pch=21, aes(color=role)) +
  scale_color_manual(values=c('blue', 'grey', 'black')) +
  geom_edge_link(aes(edge_alpha = weight)) +
  #geom_node_text(aes(label = name), repel = TRUE, size = 4) +
  theme_void() +
  labs(title = "Grantor-Grantee Relationships")

#In View of the above observation about the core vs. periphery, you could determine the centrality of each node in one of several possible ways:

#centrality measures using igraph:

#degree centrality = how many edges a node has
deg <- degree(covnet)
head(deg)
deg.df <- data.frame(deg)
#note that you could use this vector to assign color or whatever to nodes, like this:

V(covnet)$degree <- deg
#Check:
V(covnet)['WAKE MEMORIAL ASSN INC']$degree #OR
V(covnet)[1]$degree

ggraph(covnet, layout = "fr") +  
  geom_edge_link(aes(edge_alpha = weight)) +
  geom_node_point(pch=21, aes(alpha=degree)) +
  geom_edge_link(aes(edge_alpha = weight)) +
  #geom_node_text(aes(label = name), repel = TRUE, size = 4) +
  theme_void() +
  labs(title = "Grantor-Grantee Relationships and Degree Centrality")

#You could also use degree, or any of the centrality metrics below, to do a histogram and/or select 'central' nodes for further analysis.

hist(deg) #not super enlightening

deg.df <- data.frame(deg)
ggplot(filter(deg.df, deg<25), aes(deg)) +
  geom_density() #Still not super enlightening, but you get the idea.

#closeness centrality. Higher values = closer to 'center' of graph.
close <- closeness(covnet)
head(close)

#betweenness centrality, a common method
bet <- betweenness(covnet)
head(bet)


# Community detection. #RD: I don't think community detection will be helpful because I think there's more of a core-periphery structure than a set of cohesive communities. You can tell this by doing:

count_components(covnet) #Lots of small, disconnected groups


communities <- cluster_infomap(covnet)


V(covnet)$community <- membership(communities)
table(membership(communities)) #The infomap procedure is coming up with over 3000 communities. One of them has 2370 members, a couple other communities have over 100, and the rest have smaller numbers. So you *could* just look at the largest community, but I don't know whether that corresponds to the most central actors. You could also look at the communities that have around 100 members and see if they define some kind of social niche.

#Note that in addition to graphing the communities, you can just use a histogram or something to display the number of members in each community. But really, I don't think community detection is the most useful option here. 

#RD: Here are some other ideas:

cliques_list <- cliques(covnet, min=4)

cliques_list #3 cliques of actors who are all directly connected to each other

#Possibly my favorite for your data is k-coreness:
core <- coreness(covnet) #value of 8 means that you're in a subgroup where everyone has degree of at least 8. Note that in directed graphs, what looks like a single edge can actually be 2 if it goes in both directions. 

table(core)#almost all actors have values of either 1 or 2. If you're looking further into the covenants, you could focus on the actors with values of 3 or 4. Only 24 actors have value=4.

#Plot with k-core, including role
V(covnet)$coreness <- core 

ggraph(covnet, layout = "fr") +  
  geom_edge_link(aes(edge_alpha = weight)) +
  geom_node_point(pch=21, aes(color=role, alpha=coreness)) +
  geom_edge_link(aes(edge_alpha = weight)) +
  #geom_node_text(aes(label = name), repel = TRUE, size = 4) +
  theme_void() +
  labs(title = "Grantor-Grantee Relationships and k-coreness")

#You can also look at the components in the graph:
# strongly connected components (all nodes can reach all other nodes; relevant for directed graphs)
comp <- components(covnet, mode='strong')

largest <- largest_component(covnet)#gives largest component, which is very large in this case (9100 nodes)

