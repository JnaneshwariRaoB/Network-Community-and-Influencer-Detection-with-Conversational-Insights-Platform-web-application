 💬 Community Detection and Trending Topics Explorer

This is a **Streamlit** web app for uploading network data, detecting communities using the **Louvain algorithm**, identifying key influencers, and exploring trending topics discussed within those communities.



 🚀 Features

- 📂 Upload your edgelist CSV file
- 🧠 Detect communities with the **Louvain algorithm**
- 🌟 Identify top influencers in each community using centrality measures
- 🔍 Search communities by keywords/topics
- 📈 View trending topics globally and per community
- 🗺 Visualize the network with color-coded communities

---

 📂 Input Format

Upload a **CSV file** with the following required columns:

| Column         | Description                                      |
|----------------|--------------------------------------------------|
| `source`       | Node initiating the interaction                  |
| `target`       | Node receiving the interaction                   |
| `conversation` | Text or topic of the interaction                 |
| `weight` *(optional)* | Numeric value representing connection strength |

**Example CSV:**

source,target,conversation,weight
Alice,Bob,Climate Change,1
Bob,Charlie,Climate Change,2
Alice,Eve,AI Safety,1
Charlie,Dave,Quantum Computing,3


📊 How It Works

- Graph Construction: Builds a networkx graph from your CSV.

- Community Detection: Uses community-louvain to detect communities.

- Influencer Analysis: Computes degree, betweenness, and closeness centralities.

- Topic Analysis: Aggregates conversation topics per community.

- Visualization: Displays network graph with color-coded communities.
