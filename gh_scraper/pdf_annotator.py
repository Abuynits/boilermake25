from PyPDF2 import PdfWriter, PdfReader
import json
# pdfIn = "/Users/alexiy/Projects/Purdue/boilermake25/gh_scraper/data/ab_res.pdf"
# pdfOut = "/Users/alexiy/Projects/Purdue/boilermake25/gh_scraper/data/ab_out.pdf"
# Load JSON data from a file
# with open('/Users/alexiy/Projects/Purdue/boilermake25/gh_scraper/data/Abuynits.json', 'r') as file:
#     example_data = json.load(file)
import fitz  # PyMuPDF
colors = {
    "Red": [1, 0, 0],
    "Light Red": [1, .4, .4],
    "Yellow": [1, 1, 0],
    "Light Green": [.56, .93, .56],
    "Green": [0, 0.5, 0]
}
def highlight_text(pdf_path, output_path, text_color_pairs):
    doc = fitz.open(pdf_path)
    
    for page in doc:
        for txt, color in text_color_pairs:
            # remove chars that arent used
            #breakpoint()
            text_pairs_1 = txt.split(" ")[::3]
            text_pairs_2 = txt.split(" ")[1::3]
            text_pairs_3 = txt.split(" ")[2::3]
            pairs = [" ".join(i) for i in list(zip(text_pairs_1, text_pairs_2, text_pairs_3))]
            for pair in pairs:
                text_instances = page.search_for(pair)  # Find all instances of the text
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)  # Add highlight annotation
                    highlight.set_colors({"stroke":(color), "fill":color})
                    highlight.update()

    doc.save(output_path)
    print(f"Saved highlighted PDF as: {output_path}")

def annotate_resume(rated_data, pdf_in, pdf_out):
    text_color_pairs = []
    for text, rating, _ in rated_data['experience_data']:
        if rating == 1:
            text_color_pairs.append((text, colors["Red"]))
        elif rating == 2:
            text_color_pairs.append((text, colors["Light Red"]))
        elif rating == 3:
            text_color_pairs.append((text, colors["Yellow"]))
        elif rating == 4:
            text_color_pairs.append((text, colors["Light Green"]))
        elif rating == 5:
            text_color_pairs.append((text, colors["Green"]))
    for project in rated_data['project_data']:
        rating = project[3]
        
        text = project[0]['description']
        if type(text) != list:
            text = text.split('.')
        else:
            text = [t.replace('.','') for t in text if len(t) > 0]
        if len(text) == 0:
            continue
        if rating == 1:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Red"]))
        elif rating == 2:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Light Red"]))
        elif rating == 3:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Yellow"]))
        elif rating == 4:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Light Green"]))
        elif rating == 5:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Green"]))
        else:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Yellow"]))

    # Example usage
    # breakpoint()
    highlight_text(pdf_in, pdf_out, text_color_pairs)