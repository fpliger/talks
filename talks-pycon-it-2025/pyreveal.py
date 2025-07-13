from pyscript import window

TEMPLATE = """
<div class="reveal">
  <div class="slides">
    <section data-markdown>
      <textarea data-template>
        {content}
      </textarea>
    </section>
  </div>
</div>
"""

def show(filename):
    with open(filename) as f:
        content = f.read()

    slides = TEMPLATE.format(content=content)
    window.document.body.insertAdjacentHTML("beforeend", slides)

    options = window.Object()
    options.plugins = window.Array.new()
    options.plugins.push(window.RevealMarkdown)
    options.plugins.push(window.RevealHighlight)
    #options.plugins = [js.RevealMarkdown, js.RevealHighlight]
    
    window.Reveal.initialize(options)
    