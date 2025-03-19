# Network mapping script for racially restrictive covenants data

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
  rename(weight = n)

# Only keep strongest network relationships and maintain direction of deed flows
edges <- edges %>% 
  filter(weight >= 5)

network <- graph_from_data_frame(edges, directed = TRUE)

# Force-directed visualization
ggraph(network, layout = "fr") +  
  geom_edge_link(aes(edge_alpha = weight), arrow = arrow(length = unit(4, 'mm')), end_cap = circle(3, 'mm')) +
  geom_node_point(size = 5, color = "red") +
  geom_node_text(aes(label = name), repel = TRUE, size = 4) +
  theme_void() +
  labs(title = "Grantor-Grantee Relationships with 5+ Transactions")

# Community detection
communities <- cluster_infomap(network)

V(network)$community <- membership(communities)

ggraph(network, layout = "fr") +
  geom_edge_link(alpha = 0.6) +
  geom_node_point(aes(color = as.factor(community)), size = 5) +
  geom_node_text(aes(label = name), repel = TRUE, size = 4) +
  theme_void() +
  labs(title = "Community Structure",
       color = "Community")