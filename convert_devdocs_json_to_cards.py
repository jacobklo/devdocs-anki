import json, re, copy
from pathlib import Path
from typing import List

import bs4



def compare_headers(header1, header2):
  header_values = {'header': 0, 'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5, 'h6': 6}
  return header_values[header1.name] < header_values[header2.name]


result_node = [] #  : List[List[str,List[bs4.Tag]]]

def get_node_recursive(node: bs4.Tag, header: List[str]):
  if not node.contents:
    return
  
  cur_header : List[bs4.Tag] = []
  pending_elements : List[bs4.Tag] = []
  for c in node.contents:
    total_current_header = header+cur_header
    # If it is a header, this header and all the elements until another header will be a card
    if c.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header']:
      if pending_elements:
        this_card_header = '\u3009'.join([t.text for t in total_current_header])
        result_node.append([this_card_header, pending_elements])
        pending_elements = []
      
      if len(cur_header) <= 0: # add header if empty
        cur_header.append(c)
      elif cur_header[-1].name == c.name: # replace last header and move to next card
        cur_header[-1] = c
      elif compare_headers(cur_header[-1], c): # add sub-header to current bigger header
        cur_header.append(c)
      # If the new header is bigger, time to move to next card
      while len(cur_header) > 0 and not compare_headers(cur_header[-1], c):
        cur_header.pop()
      cur_header.append(c)


    elif c.name in ['p', 'ul', 'ol', 'pre', 'code', 'dl', 'table', 'figure', 'img', 'a'] or c.name == 'div' and 'class' in c.attrs and 'code-example' in c.attrs['class']:
      # If it is a text or code block, add to pending elements
      pending_elements.append(copy.copy(c))
    
    # Check if c has children
    elif c.name in ['div', 'section']:
      get_node_recursive(copy.copy(c), total_current_header)
      # c.decompose()


  if pending_elements:
    this_card_header = '\u3009'.join([t.text for t in total_current_header])
    result_node.append([this_card_header, pending_elements])
    



def devdocs_json_to_htmls():
  devdocs_json_dir = Path('output_devdocs')

  for d in devdocs_json_dir.glob('*.json'):
    with open(d, 'r', encoding='utf-8') as f:
      data: dict = json.load(f)

      for key,_ in data.items():
        key_normalized = re.sub(r'\W+', '_', key)
        with open(f'output_htmls/{d.stem}_{key_normalized}.html', 'w', encoding='utf-8') as html_file:
          html_file.write(data[key])


if __name__ == "__main__":
  with open('output_htmls/javascript_global_objects_array.html', 'r', encoding='utf-8') as f:
    soup = bs4.BeautifulSoup(f, 'html.parser')

    get_node_recursive(soup, [])
    
    with open('outout2.html', 'w', encoding='utf-8') as f:
      for r in result_node:
        f.write(f'<h6>TOCs:{r[0]}</h6>')
        for e in r[1]:
          f.write(str(e))
        f.write('<hr><hr><hr>\n\n')