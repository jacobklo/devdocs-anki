import hashlib, csv, html
from typing import List

import genanki


DefaultFrontTemplate = '''<script>

var jsKeywords = ['await', 'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default', 'delete', 'do', 'else', 'enum', 'export', 'extends', 'false', 'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof', 'new', 'null', 'return', 'super', 'switch', 'this', 'throw', 'true', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield'];

var cppKeywords = ['alignas', 'alignof', 'and', 'and_eq', 'asm', 'auto', 'bitand', 'bitor', 'bool', 'break','case', 'catch', 'char', 'char8_t', 'char16_t', 'char32_t', 'class', 'compl', 'concept','const', 'consteval', 'constexpr', 'const_cast', 'continue', 'co_await', 'co_return', 'co_yield', 'decltype', 'default', 'delete', 'do', 'double', 'dynamic_cast', 'else', 'enum', 'explicit', 'export', 'extern', 'false', 'float', 'for', 'friend', 'goto', 'if', 'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'noexcept', 'not', 'not_eq', 'nullptr', 'operator', 'or', 'or_eq', 'private', 'protected', 'public', 'register', 'reinterpret_cast', 'requires', 'return', 'short', 'signed', 'sizeof', 'static', 'static_assert', 'static_cast', 'struct', 'switch', 'template', 'this', 'thread_local', 'throw', 'true', 'try', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void', 'volatile', 'wchar_t', 'while', 'xor', 'xor_eq'];

var pythonKeywords = ['False', 'await', 'else', 'import', 'pass', 'None', 'break', 'except', 'in', 'raise', 'True', 'class', 'finally', 'is', 'return', 'and', 'continue', 'for', 'lambda', 'try', 'as', 'def', 'from', 'nonlocal', 'while', 'assert', 'del', 'global', 'not', 'with', 'async', 'elif', 'if', 'or', 'yield'];


var reactKeywords = ['import', 'export', 'from', 'return', 'class', 'extends', 'constructor', 'render', 'super', 'componentDidMount', 'componentDidUpdate', 'componentWillUnmount', 'setState', 'this', 'state', 'props', 'defaultProps'];


function obfuscatePythonCode(pre_tag) {
  let keywordSet = new Set(pythonKeywords + reactKeywords + cppKeywords + jsKeywords);
  let assignmentRegex = /(.+?)\s*((==|!=|<=|>=|<|>|=)\s*[^#\n]+)/g;

  let python_code = pre_tag.textContent;
  let result_code = python_code
    .split("\n")
    .map((line) => {
      if ( line.trim().startsWith("//") ||
        line.trim().startsWith("/*") ||
        line.trim().match(/^\/\*[\s\S]*?\*\/$/g) || 
				line.trim().startsWith("#") || 
				line.trim().startsWith("\'\'\'") || 
				line.trim().startsWith('\"\"\"') ) {
        return line;
      }
      return line.replace(
        assignmentRegex, (match, variable, expression, operator) => {
          if (keywordSet.has(variable)) { return match; }
          
          let texthidden = expression.replace(operator, '');
          let spanElement = document.createElement('span');
          spanElement.setAttribute('hidden-text', texthidden);
          spanElement.setAttribute('class', 'hidden-text');
          spanElement.textContent = '_'.repeat(texthidden.length);
          return `${variable} ${operator} ${spanElement.outerHTML}`;
        }
      );
    })
    .join("\n");
    pre_tag.innerHTML = result_code; 
}



function hideSomeText(node) {
  if (!node || !node.childNodes || node.tagName.toLowerCase() === 'pre') return;
		console.log(node.tagName);
  node.childNodes.forEach(child => {
      if (child.nodeType === Node.ELEMENT_NODE) {
          hideSomeText(child);
      }
      if (child.nodeType === Node.TEXT_NODE) {
          const parentTag = child.parentNode.tagName.toLowerCase();
          if (['b', 'i', 'u',  's', 'em', 'strong', 'code'].includes(parentTag)) {
              child.nodeValue = child.nodeValue.replace(/./g, '_');
          }
      }
  });
}

function update(prob, seed) {

  let div = document.querySelector('.question');
  let clone2 = document.querySelector('.question-clone');
  
  div.innerHTML = clone2.innerHTML;
  hideSomeText(div);
  div.querySelectorAll('code').forEach(pre => obfuscatePythonCode(pre));

  div.style.display = 'none';
  div.style.display = 'block';


  document.querySelectorAll('.hidden-text').forEach(span => {
    span.addEventListener('click', function() {
      let tmp = this.textContent;
      this.textContent = this.getAttribute('hidden-text');
      this.setAttribute('hidden-text', tmp);
    });
  });
	
}

setTimeout(() => {
	update(0.95);
}, 100);
</script>

<div class="front">

  <!-- Question will be dynamically loaded by update() -->
  <div class="question" style="display:none"></div>

  <!-- Clone the original question data, as each update() will modify and hide some text in <div question> -->
  <div class="question-clone" style="display:none">
    {{Front}}
  </div>
</div>
'''

DefaultBackTemplate = '''
<script>
var script3 = document.createElement('script');
script3.src = 'highlight.js';
script3.async = false;
document.head.appendChild(script3);
document.head.removeChild(script3);

function update(prob, seed) {

  let div = document.querySelector('.question');
  let clone2 = document.querySelector('.question-clone');
  
  div.innerHTML = clone2.innerHTML;
  
  div.style.display = 'none';
  div.style.display = 'block';

	hljs.highlightAll();
}

setTimeout(() => {
	update(0.95);
}, 100);
</script>

<link rel="stylesheet" href="monokai-sublime.css">


<div class="back">

  <!-- Question will be dynamically loaded by update() -->
  <div class="question" style="display:none"></div>

  <!-- Clone the original question data, as each update() will modify and hide some text in <div question> -->
  <div class="question-clone" style="display:none">
		{{Front}}
    {{Back}}

  </div>
</div>

'''

DefaultStyle = '''
.back {
  font-family: arial;
  font-size: 20px;
  text-align: left;
  color: white;
  background-color: black;
}

.front {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: white;
  background-color: black;
}

'''


def create_anki_package(name: str, model: genanki.Model, notes: List[genanki.Note] ):
    
    deck = genanki.Deck(deck_id=abs(hash(name)) % (10 ** 10), name=name)

    for n in notes:
      deck.add_note(n)

    # img_path = Path(r'image').glob('**/*')
    # images = ['image/'+x.name for x in img_path if x.is_file()]

    deck.add_note(genanki.Note(model=model,
        fields=['Dummy card for {{c1::javascript}} file', '<img src="highlight.js" style="display:none"><img src="monokai-sublime.css" style="display:none">']
    ))
    images = ['data/highlight.js', 'data/monokai-sublime.css'] # A hack to include Javascript file

    anki_output = genanki.Package(deck)
    anki_output.media_files = images
    anki_output.write_to_file(f'{name}.apkg')




if __name__ == "__main__":
    name = 'PythonDocs'
    hash_object = hashlib.sha1(name.encode('utf-8'))
    hex_dig = int(hash_object.hexdigest(), 16) % (10 ** 10)
    front_html = DefaultFrontTemplate
    back_html = DefaultBackTemplate

    templates = [{
      'name': f'{name}Basic',
      'qfmt': front_html,
      'afmt': back_html,
    }]
    model = genanki.Model(model_id=hex_dig, model_type=genanki.Model.FRONT_BACK, name=name, fields=[{'name': 'Front'},{'name': 'Back'}], templates=templates, css=DefaultStyle)
    # notes = csv_to_notes(['output_flashcards_with_chatgpt\stdtypes.csv'], model=model)
    create_anki_package(name, model, notes)