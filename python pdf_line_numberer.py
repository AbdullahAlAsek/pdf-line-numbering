import fitz  # PyMuPDF

def add_smart_hybrid_numbers(input_pdf_path, output_pdf_path):
    try:
        doc = fitz.open(input_pdf_path)
        global_counter = 1
        
        # --- SETTINGS ---
        # 1. Skip text larger than this (Titles)
        MAX_FONT_SIZE = 12.0  
        
        # 2. Skip text in this top margin (Running Headers)
        TOP_MARGIN_SKIP = 50  
        
        # 3. Skip keywords (Captions)
        SKIP_KEYWORDS = ["figure", "fig.", "table", "source", "caption"]
        # ----------------

        print(f"Processing {len(doc)} pages...")

        for page in doc:
            page_width = page.rect.width
            mid_point = page_width / 2
            
            # 1. Collect Valid Text Snippets
            # We flatten the entire page into a list of words to ignore block boundaries
            snippets = []
            text_data = page.get_text("dict")
            
            for block in text_data["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        # Check Font Size (First character)
                        if line["spans"]:
                            if line["spans"][0]["size"] > MAX_FONT_SIZE:
                                continue # Skip Titles

                        # Get coordinates
                        x0 = line["bbox"][0]
                        y_base = line["spans"][0]["origin"][1]
                        
                        # Check Top Margin
                        if y_base < TOP_MARGIN_SKIP:
                            continue

                        # Get text content
                        text = " ".join([s["text"] for s in line["spans"]]).strip()
                        
                        if text:
                            snippets.append({
                                'text': text,
                                'x': x0,
                                'y': y_base,
                                'center': (line["bbox"][0] + line["bbox"][2]) / 2
                            })

            if not snippets:
                continue

            # 2. Detect "Column Split Point"
            # Find the first snippet that is clearly in the "Right Column" zone.
            # We assume anything above this Y-position is the "Abstract/Header" area.
            split_y = page.rect.height # Default: No columns found
            
            # Look for text starting strictly on the right side
            for s in snippets:
                if s['x'] > mid_point: 
                    # Found a block on the right! 
                    # Use its Y position as the start of the 2-column section.
                    if s['y'] < split_y:
                        split_y = s['y']
            
            # Give a tiny buffer (e.g. 10 units) to capture the top of that line
            split_y -= 10

            # 3. Separate Snippets into Zones
            top_zone = []   # Abstract (Single Col)
            left_col = []   # Body (Left Col)
            right_col = []  # Body (Right Col)
            
            for s in snippets:
                if s['y'] < split_y:
                    top_zone.append(s)
                elif s['center'] < mid_point:
                    left_col.append(s)
                else:
                    right_col.append(s)

            # 4. Helper to Group and Number
            def process_zone(snippet_list, start_number):
                if not snippet_list:
                    return start_number
                
                # Sort strictly by vertical position
                snippet_list.sort(key=lambda s: s['y'])
                
                # Group snippets that are on the same visual line (within 3px)
                unique_rows = []
                current_row = [snippet_list[0]]
                
                for s in snippet_list[1:]:
                    last_s = current_row[-1]
                    if abs(s['y'] - last_s['y']) <= 3:
                        current_row.append(s)
                    else:
                        unique_rows.append(current_row)
                        current_row = [s]
                unique_rows.append(current_row)

                # Number the grouped rows
                current_count = start_number
                
                for row_group in unique_rows:
                    # Combine text for Keyword Check
                    full_text = " ".join([s['text'] for s in row_group]).lower()
                    
                    if any(full_text.startswith(kw) for kw in SKIP_KEYWORDS):
                        continue

                    # Find position
                    min_x = min(s['x'] for s in row_group)
                    y_pos = row_group[0]['y']
                    
                    # Draw Number
                    page.insert_text(
                        (min_x - 18, y_pos), 
                        str(current_count), 
                        fontname="helv", 
                        fontsize=8, 
                        color=(0.5, 0.5, 0.5)
                    )
                    current_count += 1
                
                return current_count

            # 5. Execute Order: Abstract -> Left Col -> Right Col
            global_counter = process_zone(top_zone, global_counter)
            global_counter = process_zone(left_col, global_counter)
            global_counter = process_zone(right_col, global_counter)

        doc.save(output_pdf_path)
        print(f"Success! Saved as {output_pdf_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# RUN THE FUNCTION
add_smart_hybrid_numbers("your_file.pdf", "output.pdf")