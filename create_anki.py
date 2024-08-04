import hashlib, csv, html
from typing import List

import genanki


DefaultFrontTemplate = '''<div class="front">{{Front}}</div>'''

DefaultBackTemplate = '''
{{Front}}

<hr>
<script>

var pythonKeywords = ['False', 'await', 'else', 'import', 'pass', 'None', 'break', 'except', 'in', 'raise', 'True', 'class', 'finally', 'is', 'return', 'and', 'continue', 'for', 'lambda', 'try', 'as', 'def', 'from', 'nonlocal', 'while', 'assert', 'del', 'global', 'not', 'with', 'async', 'elif', 'if', 'or', 'yield'];


var reactKeywords = ['import', 'export', 'from', 'return', 'class', 'extends', 'constructor', 'render', 'super', 'componentDidMount', 'componentDidUpdate', 'componentWillUnmount', 'setState', 'this', 'state', 'props', 'defaultProps'];


function obfuscateJSXCode(jsx_code) {
  const keywordSet = new Set(reactKeywords);
  const jsxAssignmentRegex = /=|=>|==|!=|<=|>=|<|>/;
  return jsx_code
    .split("\n")
    .map((line) => {
      if (
        line.trim().startsWith("//") ||
        line.trim().startsWith("/*") ||
        line.trim().match(/^\/\*[\s\S]*?\*\/$/g) ||
        line.trim().startsWith('\"\"\"') ||
        line.trim().startsWith("\'\'\'")
      ) {
        return line;
      }
      return line.replace(
        /(.+?)\s*((=>|==|!=|<=|>=|<|>|=)\s*[^#\n]+)/g,
        (match, variable, expression, operator) => {
          if (keywordSet.has(variable.trim())) {
            return match;
          }
          return `${variable} ${operator} ${'_'.repeat(expression.length - operator.length)}`;
        }
      );
    })
    .join("\n");
}

function obfuscatePythonCode(pre_tag) {
  const keywordSet = new Set(pythonKeywords);
  const assignmentRegex = /(.+?)\s*((==|!=|<=|>=|<|>|=)\s*[^#\n]+)/g;

  let python_code = pre_tag.textContent;
  let result_code = python_code
    .split("\n")
    .map((line) => {
      if ( line.trim().startsWith("#") || line.trim().startsWith("\'\'\'") || line.trim().startsWith('\"\"\"') ) {
        return line;
      }
      return line.replace(
        assignmentRegex, (match, variable, expression, operator) => {
          if (keywordSet.has(variable)) { return match; }
          
          let spanElement = document.createElement('span');
          spanElement.setAttribute('hidden-text', expression);
          spanElement.setAttribute('class', 'hidden-text');
          spanElement.textContent = '_'.repeat(expression.length - operator.length);
          return `${variable} ${operator} ${spanElement.outerHTML}`;
        }
      );
    })
    .join("\n");
    pre_tag.innerHTML = result_code; 
}


function update(prob, seed) {

  let div = document.querySelector('.question');
  let clone2 = document.querySelector('.question-clone');
  
  div.innerHTML = clone2.innerHTML;
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

<div class="back">

  <!-- Question will be dynamically loaded by update() -->
  <div class="question" style="display:none"></div>

  <!-- Clone the original question data, as each update() will modify and hide some text in <div question> -->
  <div class="question-clone" style="display:none">
<pre><code>
    {{Back}}
</code></pre>
  </div>
</div>
'''

DefaultStyle = '''
.back {
  font-family: arial;
  font-size: 16px;
  text-align: left;
  color: white;
  background-color: black;
}

.front {
  font-family: arial;
  font-size: 24px;
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

    # deck.add_note(genanki.Note(model=model,
    #     fields=['Dummy card for {{c1::javascript}} file', '<img src="highlight.js" style="display:none"><img src="monokai-sublime.css" style="display:none">']
    # ))
    images = [] # ['data/highlight.js', 'data/monokai-sublime.css'] # A hack to include Javascript file

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