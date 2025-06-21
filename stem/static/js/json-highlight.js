// JSON Syntax Highlighter
// Converts JSON strings to HTML with syntax highlighting

function highlightJSON(jsonString) {
    try {
        // Parse the JSON to validate it
        const parsed = JSON.parse(jsonString);
        const formatted = JSON.stringify(parsed, null, 2);
        
        // Escape HTML characters
        const escaped = formatted
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
        
        // Apply syntax highlighting
        const highlighted = escaped
            // Highlight keys (property names)
            .replace(/"([^"]+)":/g, '<span class="json-key">"$1"</span><span class="json-punctuation">:</span>')
            // Highlight strings
            .replace(/"([^"]*)"/g, '<span class="json-string">"$1"</span>')
            // Highlight numbers
            .replace(/\b(-?\d+\.?\d*)\b/g, '<span class="json-number">$1</span>')
            // Highlight booleans
            .replace(/\b(true|false)\b/g, '<span class="json-boolean">$1</span>')
            // Highlight null
            .replace(/\bnull\b/g, '<span class="json-null">null</span>')
            // Highlight punctuation (braces, brackets, commas)
            .replace(/([{}[\]])/g, '<span class="json-punctuation">$1</span>')
            .replace(/,/g, '<span class="json-punctuation">,</span>');
        
        return highlighted;
    } catch (error) {
        // If JSON parsing fails, return the original string with basic escaping
        return jsonString
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
}

// Function to apply highlighting to all JSON content elements
function applyJSONHighlighting() {
    const jsonElements = document.querySelectorAll('.json-content');
    jsonElements.forEach(element => {
        if (element.textContent && !element.classList.contains('highlighted')) {
            const originalText = element.textContent;
            element.innerHTML = highlightJSON(originalText);
            element.classList.add('highlighted');
        }
    });
}

// Apply highlighting when DOM is loaded
document.addEventListener('DOMContentLoaded', applyJSONHighlighting);

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { highlightJSON, applyJSONHighlighting };
} 