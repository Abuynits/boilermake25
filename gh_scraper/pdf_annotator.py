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
def get_viable_text(doc, text):
    output_text = []
    curr_text = text.split(' ')[0]
    for t in text.split(' ')[1:]:
        found_match = False
        for page in doc:
            if (f'{curr_text} {t}') in page.get_text():
                found_match = True
                break
            else:
                continue
        if found_match:
            curr_text = f'{curr_text} {t}'
        else:
            output_text.append(curr_text)
            curr_text = t
    output_text.append(curr_text)
    return output_text


def highlight_text(pdf_path, output_path, text_color_pairs):
    doc = fitz.open(pdf_path)
    
    for i, page in enumerate(doc):
        for txt, color, reasoning in text_color_pairs:

            output_text = get_viable_text(doc, txt)
            added=False
            for text in output_text:
                if len(text) <= 5:
                    continue
                text_instances = page.search_for(text)  # Find all instances of the text
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)  # Add highlight annotation
                    highlight.set_colors({"stroke":(color), "fill":color})
                    highlight.update()
                if len(text_instances) != 0:
                    rect = text_instances[0]
                    if not added:
                        page.add_text_annot((int(rect[0]-20),int(rect[1])), reasoning, icon='Note')
                        added=True
                    # annot.set_popup(text_instances[0])
    doc.save(output_path)
    # now need to read the output path
    print(f"Saved highlighted PDF as: {output_path}")

def annotate_resume(rated_data, pdf_in, pdf_out):
    text_color_pairs = []
    for text, rating, reasoning in rated_data['experience_data']:
        reasoning = reasoning.strip().split(":")[1:]
        reasoning = ":".join(reasoning)
        if rating == 1:
            text_color_pairs.append((text, colors["Red"], reasoning))
        elif rating == 2:
            text_color_pairs.append((text, colors["Light Red"], reasoning))
        elif rating == 3:
            text_color_pairs.append((text, colors["Yellow"], reasoning))
        elif rating == 4:
            text_color_pairs.append((text, colors["Light Green"], reasoning))
        elif rating == 5:
            text_color_pairs.append((text, colors["Green"], reasoning))
    for project in rated_data['project_data']:
        rating = project[3]
        reasoning = project[4]
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
                    text_color_pairs.append((t, colors["Red"], reasoning))
        elif rating == 2:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Light Red"], reasoning))
        elif rating == 3:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Yellow"], reasoning))
        elif rating == 4:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Light Green"], reasoning))
        elif rating == 5:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Green"], reasoning))
        else:
            for t in text:
                if len(t) > 0:
                    text_color_pairs.append((t, colors["Yellow"], reasoning))

    # Example usage
    breakpoint()
    highlight_text(pdf_in, pdf_out, text_color_pairs)