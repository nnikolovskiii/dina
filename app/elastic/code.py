import logging
import uuid
from time import sleep
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError

ES_HOST = "http://localhost:9200"
es_client = Elasticsearch(hosts=[ES_HOST])

INDEX_NAME = "my_rag_documents"
TEXT_FIELD = "content"


def check_connection(client: Elasticsearch):
    """Check if connection to Elasticsearch is successful."""
    if client.ping():
        print("Successfully connected to Elasticsearch!")
    else:
        print("Could not connect to Elasticsearch. Check if it's running.")
        exit()


def create_index_if_not_exists(client: Elasticsearch, index: str):
    """Creates an Elasticsearch index if it doesn't exist."""
    try:
        if client.indices.exists(index=index):
            print(f"Index '{index}' already exists.")
            return

        mapping = {
            "properties": {
                TEXT_FIELD: {"type": "text"},  # This field will use BM25
                "source": {"type": "keyword"}
            }
        }
        logging.info(f"Creating index '{index}'...")
        client.indices.create(index=index, mappings=mapping)
        logging.info(f"Index '{index}' created successfully.")

    except RequestError as e:
        print(f"Error creating index '{index}': {e.info['error']['root_cause']}")
    except Exception as e:
        print(f"An unexpected error occurred during index creation: {e}")


def index_documents(client: Elasticsearch, index: str, documents: list):
    """Indexes a list of documents into Elasticsearch."""
    print(f"Indexing {len(documents)} documents into '{index}'...")
    operations = []
    for i, doc in enumerate(documents):
        operations.append({"index": {"_index": index, "_id": str(uuid.uuid4())}})
        operations.append(doc)

    if operations:
        response = client.bulk(index=index, operations=operations, refresh=True)
        if response["errors"]:
            print("Errors occurred during bulk indexing:")
            for item in response["items"]:
                if "error" in item.get("index", {}):
                    print(f"  Document ID {item['index']['_id']}: {item['index']['error']}")
        else:
            print(f"Successfully indexed {len(documents)} documents.")


def search_documents_bm25(client: Elasticsearch, index: str, query_text: str, top_k: int = 5):
    """Performs a keyword search using BM25 (via match query)."""
    print(f"\nSearching for: '{query_text}' using BM25 (default match query)")
    try:
        query = {
            "query": {
                "match": {
                    TEXT_FIELD: {
                        "query": query_text
                    }
                }
            }
        }

        response = client.search(index=index, body=query, size=top_k)

        results = []
        logging.info(f"Found {response['hits']['total']['value']} total hits.")
        logging.info(f"Returning top {len(response['hits']['hits'])} results:")

        for hit in response['hits']['hits']:
            results.append({
                "id": hit['_id'],
                "score": hit['_score'],
                "content": hit['_source'].get(TEXT_FIELD),
                "source": hit['_source'].get("source")
            })
            logging.info(f"  ID: {hit['_id']}, Score: {hit['_score']:.4f}, Source: {hit['_source'].get('source')}")

        return results

    except NotFoundError:
        print(f"Error: Index '{index}' not found.")
        return []
    except RequestError as e:
        print(f"Error executing search: {e.info['error']['root_cause']}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during search: {e}")
        return []


def delete_documents(client: Elasticsearch, index: str, doc_id: str = None, query: dict = None):
    """
    Deletes documents from Elasticsearch index.

    Args:
        client: Elasticsearch client
        index: Name of the index
        doc_id: Specific document ID to delete (if provided)
        query: Query to match documents for deletion (if provided)

    Returns:
        Dictionary with deletion results
    """
    try:
        if doc_id:
            # Delete a specific document by ID
            print(f"Deleting document with ID: {doc_id} from index '{index}'")
            response = client.delete(index=index, id=doc_id, refresh=True)
            print(f"Document deleted successfully: {response['result']}")
            return response

        elif query:
            # Delete documents matching a query
            print(f"Deleting documents matching query from index '{index}'")
            response = client.delete_by_query(index=index, query=query, refresh=True)
            print(f"Successfully deleted {response['deleted']} documents")
            return response

        else:
            print("Error: Either doc_id or query must be provided")
            return {"error": "Either doc_id or query must be provided"}

    except NotFoundError:
        print(f"Error: Document or index '{index}' not found")
        return {"error": f"Document or index '{index}' not found"}
    except RequestError as e:
        print(f"Error executing deletion: {e.info['error']['root_cause']}")
        return {"error": str(e.info['error']['root_cause'])}
    except Exception as e:
        print(f"An unexpected error occurred during deletion: {e}")
        return {"error": str(e)}

# --- Main Execution ---
if __name__ == "__main__":
    check_connection(es_client)
    create_index_if_not_exists(es_client, INDEX_NAME)

    # Sample documents (in a real RAG, these would be chunks from your knowledge base)
    sample_docs = [
        {TEXT_FIELD: "The quick brown fox jumps over the lazy dog."},
        {TEXT_FIELD: "Elasticsearch is a distributed search and analytics engine based on Lucene.",
         "source": "elastic_intro.pdf"},
        {
            TEXT_FIELD: "BM25 is a ranking function used by search engines to rank matching documents according to their relevance.",
            "source": "search_algorithms.txt"},
        {TEXT_FIELD: "Retrieval Augmented Generation (RAG) combines pre-trained models with retrieval systems.",
         "source": "rag_paper.pdf"},
        {TEXT_FIELD: "A lazy brown dog was sleeping.", "source": "doc_2.txt"},
        {TEXT_FIELD: "Okapi BM25 improves upon TF-IDF for relevance ranking.", "source": "search_algorithms.txt"},
        {TEXT_FIELD: "Python's elasticsearch-py library allows interaction with the search engine.",
         "source": "python_docs.html"}
    ]

    # Index the documents (only needs to be done once, or when data changes)
    # Check if index is empty before indexing to avoid duplicates if run multiple times
    count_response = es_client.count(index=INDEX_NAME)
    if count_response['count'] == 0:
        index_documents(es_client, INDEX_NAME, sample_docs)
        # Give Elasticsearch a moment to finish indexing/refreshing, especially after bulk
        sleep(2)
    else:
        print(f"Index '{INDEX_NAME}' already contains documents. Skipping indexing.")

    # --- Perform Keyword Search (using BM25) ---
    user_query = "search engine ranking algorithms"
    retrieved_docs = search_documents_bm25(es_client, INDEX_NAME, user_query, top_k=3)

    print("\n--- Retrieved Documents (for RAG context) ---")
    if retrieved_docs:
        for doc in retrieved_docs:
            print(f"Score: {doc['score']:.4f} | Source: {doc['source']} | Content: {doc['content']}")
        # In a RAG pipeline, you would format this content and pass it to the LLM:
        context_for_llm = "\n\n".join([doc['content'] for doc in retrieved_docs])
        print("\n--- Context to potentially pass to LLM ---")
        print(context_for_llm)
    else:
        print("No documents found for the query.")

    print("\n--- Another Example ---")
    user_query_2 = "lazy dog"
    retrieved_docs_2 = search_documents_bm25(es_client, INDEX_NAME, user_query_2, top_k=2)
    # Process results as above...

    # match_all_query = {"match_all": {}}
    # delete_result = delete_documents(es_client, INDEX_NAME, query=match_all_query)
    # print(delete_result)
