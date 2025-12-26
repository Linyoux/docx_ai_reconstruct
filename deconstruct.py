import os
import zipfile
import re
import shutil
from PIL import Image, ImageDraw, ImageFont
from math import ceil

def natural_sort_key(s):
    """
    实现自然排序的关键函数。
    将字符串拆分为数字和非数字部分，使得 'image2.png' 排在 'image10.png' 之前。
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def create_visual_reference_pdf(image_files, media_dir, output_pdf_path):
    """
    将图片列表生成为一个 PDF，每页包含文件名和图片。
    """
    pdf_pages = []
    
    # A4 尺寸 (72 DPI) -> 595 x 842 像素 (可根据需要调大分辨率)
    page_width, page_height = 595, 842
    margin = 50
    
    # 尝试加载一个字体，如果没有则使用默认
    try:
        # Windows 常见字体路径，Mac/Linux 可能需要调整
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()

    for filename in image_files:
        img_path = os.path.join(media_dir, filename)
        
        try:
            # 创建纯白背景页
            page = Image.new('RGB', (page_width, page_height), (255, 255, 255))
            draw = ImageDraw.Draw(page)
            
            # 1. 写入文件名 (ID)
            text = f"ID: {filename}"
            # 使用 textbbox 获取文本尺寸 (Pillow >= 9.2.0)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            draw.text(((page_width - text_w) / 2, margin), text, fill=(0, 0, 0), font=font)
            
            # 2. 处理图片
            src_img = Image.open(img_path)
            
            # 计算缩放比例，保持长宽比，放入页面中心
            max_img_w = page_width - 2 * margin
            max_img_h = page_height - 3 * margin - text_h
            
            src_img.thumbnail((max_img_w, max_img_h), Image.Resampling.LANCZOS)
            
            # 粘贴图片
            img_x = int((page_width - src_img.width) / 2)
            img_y = int(margin + text_h + 20) # 放在文字下方 20px
            
            # 如果图片有透明通道(RGBA)，需要粘贴到白色背景上
            if src_img.mode == 'RGBA':
                page.paste(src_img, (img_x, img_y), src_img)
            else:
                page.paste(src_img, (img_x, img_y))
            
            pdf_pages.append(page)
            
        except Exception as e:
            print(f"警告: 无法处理图片 {filename}. 错误: {e}")

    # 保存 PDF
    if pdf_pages:
        pdf_pages[0].save(
            output_pdf_path, "PDF", resolution=100.0, 
            save_all=True, append_images=pdf_pages[1:]
        )
        print(f"生成参考文档: {output_pdf_path} ({len(pdf_pages)} 页)")

def process_docx(docx_path, output_dir):
    """
    主处理流程
    """
    # 1. 准备目录
    doc_name = os.path.splitext(os.path.basename(docx_path))[0]
    media_extract_dir = os.path.join(output_dir, doc_name, "media_source")
    pdf_output_dir = os.path.join(output_dir, doc_name, "visual_refs")
    
    if os.path.exists(media_extract_dir):
        shutil.rmtree(media_extract_dir)
    os.makedirs(media_extract_dir)
    os.makedirs(pdf_output_dir)

    print(f"正在处理: {docx_path} ...")

    # 2. 解压 Docx (提取图片)
    with zipfile.ZipFile(docx_path, 'r') as z:
        for file_info in z.infolist():
            if file_info.filename.startswith('word/media/'):
                z.extract(file_info, media_extract_dir)

    # 3. 获取所有图片并自然排序
    # Word 解压后的路径是 media_extract_dir/word/media/
    actual_media_dir = os.path.join(media_extract_dir, 'word', 'media')
    
    if not os.path.exists(actual_media_dir):
        print("未在文档中发现图片文件。")
        return

    all_files = os.listdir(actual_media_dir)
    # 过滤非图片文件 (可根据需要添加更多格式)
    valid_exts = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.emf', '.wmf'}
    image_files = [f for f in all_files if os.path.splitext(f)[1].lower() in valid_exts]
    
    # --- 核心逻辑：自然排序 ---
    image_files.sort(key=natural_sort_key)
    
    print(f"共提取 {len(image_files)} 张图片。")

    # 4. 分块并生成 PDF (每份最多 100 页)
    CHUNK_SIZE = 100
    total_chunks = ceil(len(image_files) / CHUNK_SIZE)

    for i in range(total_chunks):
        start_idx = i * CHUNK_SIZE
        end_idx = start_idx + CHUNK_SIZE
        chunk_files = image_files[start_idx:end_idx]
        
        pdf_name = f"{doc_name}_VisualRef_Part{i+1}.pdf"
        pdf_path = os.path.join(pdf_output_dir, pdf_name)
        
        create_visual_reference_pdf(chunk_files, actual_media_dir, pdf_path)

    print(f"处理完成！所有资源已保存至: {output_dir}/{doc_name}")

# --- 使用示例 ---
if __name__ == "__main__":
    # 在这里修改你的输入文件路径
    input_docx = "input.docx" 
    output_folder = "./pipeline_output"
    
    # 简单的检查文件是否存在
    if not os.path.exists(input_docx):
        # 为了演示，创建一个假文件或者报错
        print(f"错误: 找不到文件 {input_docx}")
    else:
        process_docx(input_docx, output_folder)