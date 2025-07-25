import streamlit as st
import pandas as pd
import networkx as nx
from community import community_louvain
from collections import Counter
import matplotlib.pyplot as plt

# Streamlit Title and Description
st.title("💬 Community Analysis and Topic Explorer")
st.markdown("""
Welcome to the **Community Detection and Trending Topics Explorer**!  
Analyze communities, identify influencers, and explore trending topics across your network data.
""")

# File Upload Section
uploaded_file = st.sidebar.file_uploader("Upload an edgelist CSV file", type="csv")

if uploaded_file:
    try:
        # Load and Validate CSV Data
        df = pd.read_csv(uploaded_file)
        required_columns = {'source', 'target', 'conversation'}
        if not required_columns.issubset(df.columns):
            st.error(f"CSV file must contain the following columns: {', '.join(required_columns)}")
        else:
            st.success("File successfully uploaded and validated!")

            # Create a Graph
            G = nx.Graph()
            for _, row in df.iterrows():
                G.add_edge(row['source'], row['target'], weight=row.get('weight', 1))

            # Community Detection with Louvain
            partition = community_louvain.best_partition(G, random_state=42)
            nx.set_node_attributes(G, partition, 'community')

            # Organize Communities and Topics
            communities = {}
            community_topics = {}
            for node, community_id in partition.items():
                communities.setdefault(community_id, []).append(node)

            for _, row in df.iterrows():
                source_community = partition[row['source']]
                community_topics.setdefault(source_community, []).append(row['conversation'])

            # Define Influencer Finding Function
            def find_influencers(graph, community_ids):
                if not isinstance(community_ids, list):
                    community_ids = [community_ids]

                influencers = {}
                for community_id in community_ids:
                    community_nodes = [n for n, d in graph.nodes(data=True) if d.get('community') == community_id]
                    subgraph = graph.subgraph(community_nodes)

                    # Centrality Measures
                    degree_centrality = nx.degree_centrality(subgraph)
                    betweenness_centrality = nx.betweenness_centrality(subgraph)
                    closeness_centrality = nx.closeness_centrality(subgraph)

                    # Combined Ranking
                    combined_centrality = {
                        node: (degree_centrality[node] + betweenness_centrality[node] + closeness_centrality[node]) / 3
                        for node in community_nodes
                    }
                    top_influencer = max(combined_centrality.items(), key=lambda x: x[1])[0]
                    influencers[community_id] = top_influencer

                return influencers

            # Influencers and Topics
            influencers = find_influencers(G, list(communities.keys()))

            # Navigation Bar
            st.sidebar.header("Navigation")
            nav_option = st.sidebar.radio(
                "Choose a feature",
                ["Communities & Insights", "Topic Search", "Trending Topics"]
            )

            if nav_option == "Communities & Insights":
                # Community Selection for Details
                st.subheader("🌟 Explore Communities and Insights")
                community_id = st.selectbox("Select a Community", list(communities.keys()))

                st.markdown(f"#### ⭐ Influencer in Community {community_id}:")
                st.write(f"- **Top Influencer**: {influencers[community_id]}")

                st.markdown(f"#### 🔥 Trending Topics in Community {community_id}:")
                trending_topics = Counter(community_topics[community_id]).most_common()
                for topic, count in trending_topics:
                    st.markdown(f"- **{topic}**: {count} mentions")

                # Visualizing the Community
                st.subheader("📍 Community Visualization")
                pos = nx.spring_layout(G)
                plt.figure(figsize=(12, 10))
                community_colors = [partition[node] for node in G.nodes()]
                nx.draw(
                    G, pos,
                    with_labels=True,
                    node_color=community_colors,
                    node_size=300,
                    font_size=8,
                    cmap=plt.cm.rainbow,
                    edge_color="gray"
                )
                plt.title(f"Network Graph Highlighting Community {community_id}", fontsize=16)
                st.pyplot(plt)

            elif nav_option == "Topic Search":
                # Topic Search Section
                st.subheader("🔍 Search Communities by Topic")
                search_topic = st.text_input("Enter a topic to search:")

                if search_topic:
                    topic_communities = []
                    for community_id, topics in community_topics.items():
                        if any(search_topic.lower() in topic.lower() for topic in topics):
                            topic_communities.append(community_id)

                    if topic_communities:
                        st.markdown(f"### Communities discussing **'{search_topic}'**:")
                        for community_id in topic_communities:
                            st.markdown(f"- **Community {community_id}** ({len(communities[community_id])} nodes)")
                    else:
                        st.warning(f"No communities found discussing '{search_topic}'.")

            elif nav_option == "Trending Topics":
                # Trending Topics Section
                st.subheader("📈 Trending Topics Across All Communities")
                all_topics = [topic for topics in community_topics.values() for topic in topics]
                trending_topics_global = Counter(all_topics).most_common()

                st.markdown("### 🌟 Top Trending Topics:")
                if trending_topics_global:
                    for i, (topic, count) in enumerate(trending_topics_global, 1):
                        st.markdown(f"{i}. **{topic}** - {count} mentions")
                else:
                    st.write("No trending topics found.")

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Upload a CSV file to get started!")
