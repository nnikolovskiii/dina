import asyncio
from app.databases.qdrant_db import QdrantDatabase
import numpy as np
from sklearn.manifold import TSNE
import plotly.express as px

async def visualize(link: str):
    qdb = QdrantDatabase()
    records = {}
    async for data in qdb.scroll(
        collection_name="DocsChunk",
        filter={("base_url", "value") : link}
    ):
        for elem in data:
            key = elem.payload["id"]
            records[key] = (elem.vector, elem.payload["link"])

    data_list = [elem[0] for elem in list(records.values())]
    labels = [elem[1] for elem in list(records.values())]
    data = np.array(data_list)
    tsne = TSNE(n_components=2, random_state=42)
    data_2d = tsne.fit_transform(data)

    fig = px.scatter(
        x=data_2d[:, 0],
        y=data_2d[:, 1],
        # color=labels,
        title="t-SNE visualization",
        labels={'x': 'Dimension 1', 'y': 'Dimension 2'},
        hover_name=labels
    )

    fig.show()

asyncio.run(visualize("https://ai.pydantic.dev"))