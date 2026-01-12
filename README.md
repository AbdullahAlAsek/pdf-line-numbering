# PDF Line Numbering

This Python tool automatically adds line numbers to PDF documents. It is designed to handle complex academic layouts, including:
* Single-column abstracts mixed with double-column bodies.
* Skipping large titles and headers.
* Preventing "inline" numbers by grouping text rows smarty.

## Installation

1.  Clone this repository.
2.  Install the required library:
    `pip install -r requirements.txt`

## Usage

1.  Place your PDF file in the same folder as the script.
2.  Open `pdf_line_numberer.py` and change the filename at the bottom:
    `add_smart_hybrid_numbers("your_file.pdf", "output.pdf")`
3.  Run the script:
    `python pdf_line_numberer.py`
