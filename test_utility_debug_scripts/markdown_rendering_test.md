# Markdown Rendering Test Examples

Here are examples of markdown content that should now render properly in the chat interface:

## Test Message 1: Basic Formatting

```
# This is a main heading

This is a paragraph with **bold text** and *italic text*.

## This is a subheading

Here's a list:
- First item
- Second item with `inline code`
- Third item

1. Numbered list item
2. Another numbered item
3. Final item

Here's a code block:

```python
def hello_world():
    print("Hello, World!")
    return True
```

> This is a blockquote
> It can span multiple lines

### Key Features

- **Headers**: H1, H2, H3 with proper sizing
- **Lists**: Both bullet and numbered
- **Code**: Inline `code` and code blocks
- **Emphasis**: *italic* and **bold** text
- **Blockquotes**: For highlighting important information

## Test Message 2: Complex Example

Here's how to implement a **consensus algorithm**:

### Steps:
1. **Collect responses** from multiple AI models
2. **Analyze** the responses for:
   - Consistency
   - Accuracy 
   - Completeness
3. **Generate consensus** based on agreement

### Code Example:
```javascript
async function getConsensus(models, prompt) {
  const responses = await Promise.all(
    models.map(model => model.query(prompt))
  );
  
  return analyzeConsensus(responses);
}
```

### Important Notes:
> Always validate the consensus results before presenting them to users.

**Benefits:**
- Higher accuracy
- Reduced bias
- More comprehensive answers

*This approach ensures better AI responses through multi-model validation.*
```
