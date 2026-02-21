from duckduckgo_search import DDGS
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

def search_book_info(book_title: str) -> str:
    """
    Searches the web for information about the given book.
    Returns a concatenated string of search results.
    """
    query = f"《{book_title}》书籍 内容简介 作者核心观点 金句"
    
    results_text = ""
    try:
        with DDGS() as ddgs:
            # Get up to 5 results
            results = ddgs.text(query, max_results=5)
            for r in results:
                title = r.get("title", "")
                body = r.get("body", "")
                results_text += f"Title: {title}\nSummary: {body}\n\n"
    except Exception as e:
        print(f"Error during search: {e}")
        # Return a fallback or empty text if search fails
        results_text = f"Could not perform web search for {book_title}. Error: {e}"
        
    return results_text
