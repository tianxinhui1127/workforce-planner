import fitz
import os



def extract_images_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pdf_dir = os.path.dirname(pdf_path)
    for page_num in range(doc.page_count):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            img_name = f"page_{page_num + 1}_img_{img_index + 1}.png"
            img_path = os.path.join(pdf_dir, img_name)

            if pix.colorspace is None:
                pix.save(img_path)
            elif pix.colorspace.name == "RGB":
                pix.save(img_path)
            elif pix.colorspace.name == "GRAY":
                pix.save(img_path)
            else:
                new_pix = fitz.Pixmap(fitz.csRGB, pix)
                new_pix.save(img_path)
                new_pix = None

            pix = None
    doc.close()
    print("操作完成")


if __name__ == "__main__":
    pdf_file_path = "C:/Users/市场开发技术组/Desktop/国能西部能源青松新疆矿业有限公司大平滩煤矿选煤厂运煤道路工程/运煤道路图纸\第一册.pdf"
    extract_images_from_pdf(pdf_file_path)
 
 
 
 
 
 
