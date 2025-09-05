import streamlit as st
import pandas as pd
import networkx as nx
from community import community_louvain
from collections import Counter
import matplotlib.pyplot as plt
from textblob import TextBlob

# Streamlit Title and Description
st.title("💬 Community Analysis and Topic Explorer")
st.markdown("""
Welcome to the *Community Detection and Trending Topics Explorer*!  
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
            nav_option = st.sidebar.radio("Navigation", ["Communities & Insights", "Topic Search", "Sentiment Analysis"])

            if nav_option == "Communities & Insights":
                # Community Selection for Details
                st.subheader("🌟 Explore Communities and Insights")
                community_id = st.selectbox("Select a Community", list(communities.keys()))

                st.markdown(f"#### ⭐ Influencer in Community {community_id}:")
                st.write(f"- *Top Influencer*: {influencers[community_id]}")

                st.markdown(f"#### 🔥 Trending Topics in Community {community_id}:")
                trending_topics = Counter(community_topics[community_id]).most_common()

                st.bar_chart(pd.DataFrame(trending_topics, columns=["Topic", "Frequency"]).set_index("Topic"))
                for topic, count in trending_topics:
                    st.markdown(f"- *{topic}*: {count} mentions")

                # Visualizing the Community
                
                st.subheader("📍 Community Influence Visualization")
                community_nodes = [node for node in communities[community_id]]
                subgraph = G.subgraph(community_nodes)

                # Node size based on centrality
                degree_centrality = nx.degree_centrality(subgraph)
                node_sizes = [1000 * degree_centrality[node] for node in subgraph.nodes()]

                # Edge thickness based on weight (if weight exists)
                edge_weights = nx.get_edge_attributes(subgraph, "weight")
                edge_thickness = [edge_weights.get(edge, 1) for edge in subgraph.edges()]

                # Draw the graph
                pos = nx.spring_layout(subgraph)
                plt.figure(figsize=(10, 8))
                nx.draw_networkx_edges(subgraph, pos, alpha=0.3, width=edge_thickness)
                nx.draw_networkx_nodes(
                    subgraph, pos,
                    node_color=["red" if node == influencers[community_id] else "blue" for node in subgraph.nodes()],
                    node_size=node_sizes,
                    cmap=plt.cm.Blues,
                    alpha=0.8
                )
                nx.draw_networkx_labels(subgraph, pos, font_size=10)
                plt.title(f"Community {community_id} Influence Graph", fontsize=16)
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
                        st.markdown(f"### Communities discussing *{search_topic}*:")
                        for community_id in topic_communities:
                            st.markdown(f"- *Community {community_id}* ({len(communities[community_id])} nodes)")

                            # Graph Visualization for Topic Communities
                            st.markdown(f"#### Community {community_id} Visualization")
                            community_nodes = [node for node in communities[community_id]]
                            subgraph = G.subgraph(community_nodes)

                            # Node size based on centrality
                            degree_centrality = nx.degree_centrality(subgraph)
                            node_sizes = [1000 * degree_centrality[node] for node in subgraph.nodes()]

                            # Draw the graph
                            pos = nx.spring_layout(subgraph)
                            plt.figure(figsize=(10, 8))
                            nx.draw_networkx_nodes(
                                subgraph, pos,
                                node_color=["red" if node == influencers[community_id] else "blue" for node in subgraph.nodes()],
                                node_size=node_sizes,
                                cmap=plt.cm.Blues,
                                alpha=0.8
                            )
                            nx.draw_networkx_edges(subgraph, pos, alpha=0.3)
                            nx.draw_networkx_labels(subgraph, pos, font_size=10)
                            plt.title(f"Community {community_id} Influence Graph", fontsize=16)
                            st.pyplot(plt)
                    else:
                        st.warning(f"No communities found discussing '{search_topic}'.")

            elif nav_option == "Sentiment Analysis":
                # Sentiment Analysis Section
                st.subheader("📊 Sentiment Analysis of Conversations")
                sentiment_data = []
                for community_id, topics in community_topics.items():
                    for topic in topics:
                        analysis = TextBlob(topic)
                        polarity = analysis.sentiment.polarity
                        sentiment = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
                        sentiment_data.append({
                            "Community": community_id,
                            "Topic": topic,
                            "Sentiment": sentiment,
                            "Polarity": polarity
                        })

                sentiment_df = pd.DataFrame(sentiment_data)

                # Display overall sentiment distribution
                st.markdown("### Overall Sentiment Distribution")
                sentiment_counts = sentiment_df['Sentiment'].value_counts()
                st.bar_chart(sentiment_counts)

                # Display sentiment by community
                st.markdown("### Sentiment by Community")
                community_id = st.selectbox("Select a Community for Sentiment Analysis", list(communities.keys()))
                community_sentiment = sentiment_df[sentiment_df['Community'] == community_id]

                # Add color-coded table for sentiment
                def color_sentiment(row):
                    if row['Sentiment'] == 'Positive':
                        return ['background-color: rgb(8, 50, 107)'] * len(row)
                    elif row['Sentiment'] == 'Negative':
                        return ['background-color: rgb(213, 51, 7)'] * len(row)
                    else:
                        return ['background-color: rgb(12, 169, 52)'] * len(row)

                styled_table = community_sentiment.style.apply(color_sentiment, axis=1)

                # Configure the display settings for full area utilization
                st.markdown("""
                <style>
                    .block-container {
                    padding: 1rem 2rem 1rem 2rem;
                }
                    .dataframe-container {
                    overflow: auto;
                    max-height: 700px;
                }
                </style>
                """, unsafe_allow_html=True)

                # Render the table in a scrollable, full-area container
                st.markdown("### Sentiment Analysis Table")
                st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                st.dataframe(
                    styled_table,
                    use_container_width=True,
                    height=700  # Adjust vertical height to fully display table
                )
                st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Upload a CSV file to get started!")
