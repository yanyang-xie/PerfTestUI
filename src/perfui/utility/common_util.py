import re

def get_test_content_number(content_names):
    if content_names.find('[') < 0:
        return content_names.split('_')[-1]
    
    p = r'.*\[(\d+)~(\d+)\]/*\S*'  # match test_[1,13]
    t = re.findall(p, content_names.strip())
    if len(t) > 0:
        return t[0][1]
    else:
        return 0