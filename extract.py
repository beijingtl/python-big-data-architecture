import zipfile
import xml.etree.ElementTree as ET
import sys
import re

def extract_text_from_docx(docx_path):
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            texts = []
            for para in tree.findall('.//w:p', ns):
                para_text = ''
                for run in para.findall('.//w:r', ns):
                    for child in run:
                        if child.tag == f"{{{ns['w']}}}t" and child.text:
                            para_text += child.text
                        elif child.tag == f"{{{ns['w']}}}tab":
                            para_text += '\t'
                if para_text.strip():
                    texts.append(para_text.strip())
            return '\n'.join(texts)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    mode = sys.argv[1]
    path = sys.argv[2]
    
    text = extract_text_from_docx(path)
    if mode == 'preface':
        print(text)
    elif mode == 'toc':
        cleaned = []
        for line in text.split('\n'):
            line = line.strip()
            # If there's a tab, take everything before the last tab (which usually separates the page number)
            if '\t' in line:
                line = line.rsplit('\t', 1)[0].strip()
            else:
                # Fallback: remove trailing digits if they seem to be page numbers without space
                # But only if it's a very long string or looks like a toc entry
                # Let's see if \t fixes it first
                pass
                
            if re.match(r'^(第[0-9一二三四五六七八九十百]+章|[0-9]+(\.[0-9]+)*)\s*(.*)', line):
                # Remove trailing page numbers if they are separated by space
                line = re.sub(r'\s+[0-9]+$', '', line)
                cleaned.append(line)
        print('\n'.join(cleaned))
