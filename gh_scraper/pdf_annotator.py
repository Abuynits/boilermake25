from PyPDF2 import PdfWriter, PdfReader



pdfIn = "/Users/alexiy/Projects/Purdue/boilermake25/gh_scraper/data/ab_res.pdf"
pdfOut = "/Users/alexiy/Projects/Purdue/boilermake25/gh_scraper/data/ab_out.pdf"

import fitz  # PyMuPDF

def highlight_text(pdf_path, output_path, search_text):
    doc = fitz.open(pdf_path)
    
    for page in doc:
        for txt in search_text:
            text_instances = page.search_for(txt)  # Find all instances of the text
            for inst in text_instances:
                page.add_highlight_annot(inst)  # Add highlight annotation

    doc.save(output_path)
    print(f"Saved highlighted PDF as: {output_path}")

example_data =         {
    "title": "Robotics Mini-Projects",
    "technologies": ["Pytorch", "Gazebo", "Pybullet", "ROS"],
    "dates": "Jan 2024 - May 2024",
    "description": [
        "Implement (bi)RRT, (bi)RRTConnect, RRT* for cars and 6-DOF arms",
        "Iterative/Analytic PID for Quadruped robots and 2-DOF arms",
        "MPNet in 2D/3D environments",
        "VPG for 2-DOF arm"
    ]
}
# need to convert all info to a string
all_text_data = []
for key, value in example_data.items():
    if key in ['technologies', 'dates']:
        continue
    if isinstance(value, list):
        for i, item in enumerate(value):
            all_text_data.append(item)
    else:
        all_text_data.append(value)

# Example usage
highlight_text(pdfIn, pdfOut, all_text_data)
