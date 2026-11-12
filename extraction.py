import os

import fitz  # loading and parsing PDFs (PyMuPDF)
import requests  # sending HTTP requests


def extract_texts_from_pdfs(input_uris, first_page=1, last_page=None):
    # page parameters are optional and 1-based inclusive; by default the whole document is parsed

    texts = []

    for input_uri in input_uris:

        input_uri = str(input_uri).replace('"', "")  # removes quotation marks, common for Windows 10 file path pastes

        if input_uri.startswith(("http://", "https://")) and ".pdf" in input_uri:  # checks if input is a PDF URL
            response = requests.get(input_uri, timeout=60)
            response.raise_for_status()
            doc = fitz.open("pdf", response.content)

        elif os.path.isfile(input_uri):  # checks if input is a file path
            doc = fitz.open(input_uri)

        else:
            raise ValueError(f"Invalid URL or file path of PDF: {input_uri}")

        text = ""

        num_pages = len(doc)
        start = max(first_page - 1, 0)  # adjusted for 0-based indexing
        # Exclusive end index. The original used num_pages - 1 here, which silently
        # dropped the last page when parsing a whole document. Single-page ranges
        # such as (2, 2), which the thesis experiments used, behave the same as before.
        end = min(last_page, num_pages) if last_page is not None else num_pages

        for page_number in range(start, end):  # combining text from the document page-by-page
            page = doc.load_page(page_number)
            text += page.get_text()

        doc.close()

        texts.append(text)  # added into a list of plain text blobs

    return texts
