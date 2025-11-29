#!/usr/bin/env python3
"""
Markdown to HTML converter script.
Usage:
    python md2h.py          # Convert all .md files in current directory
    python md2h.py -r       # Convert all .md files in current directory and subdirectories
"""

import sys
import glob
from pathlib import Path


def convert_md_to_html(md_content):
    """
    Simple Markdown to HTML converter.
    Supports: headers, bold, italic, code blocks, inline code, links, images, lists.
    """
    html_lines = []
    in_code_block = False
    in_list = False

    lines = md_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                lang = line.strip()[3:].strip()
                html_lines.append(f'<pre><code class="{lang}">')
            else:
                in_code_block = False
                html_lines.append('</code></pre>')
            i += 1
            continue

        if in_code_block:
            html_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            i += 1
            continue

        # Headers
        if line.startswith('#'):
            level = 0
            while level < len(line) and line[level] == '#':
                level += 1
            if level <= 6 and level < len(line) and line[level] == ' ':
                content = line[level+1:].strip()
                content = apply_inline_formatting(content)
                html_lines.append(f'<h{level}>{content}</h{level}>')
                i += 1
                continue

        # Unordered lists
        if line.strip().startswith(('- ', '* ', '+ ')):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = line.strip()[2:].strip()
            content = apply_inline_formatting(content)
            html_lines.append(f'  <li>{content}</li>')
            i += 1
            continue

        # Ordered lists
        if line.strip() and line.strip()[0].isdigit() and '. ' in line.strip()[:4]:
            if not in_list:
                html_lines.append('<ol>')
                in_list = 'ol'
            content = line.strip().split('. ', 1)[1]
            content = apply_inline_formatting(content)
            html_lines.append(f'  <li>{content}</li>')
            i += 1
            continue

        # Close list if we're in one and hit a non-list line
        if in_list and not line.strip().startswith(('- ', '* ', '+ ')) and not (line.strip() and line.strip()[0].isdigit()):
            if in_list == 'ol':
                html_lines.append('</ol>')
            else:
                html_lines.append('</ul>')
            in_list = False

        # Empty lines
        if not line.strip():
            html_lines.append('<br>')
            i += 1
            continue

        # Regular paragraphs
        if line.strip():
            content = apply_inline_formatting(line)
            html_lines.append(f'<p>{content}</p>')

        i += 1

    # Close any open lists
    if in_list:
        if in_list == 'ol':
            html_lines.append('</ol>')
        else:
            html_lines.append('</ul>')

    return '\n'.join(html_lines)


def apply_inline_formatting(text):
    """Apply inline formatting: bold, italic, code, links, images."""
    import re

    # Images: ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', r'<img src="\2" alt="\1">', text)

    # Links: [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)

    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Italic: *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)

    # Inline code: `code`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    return text


def create_html_template(title, body_content):
    """Create a complete HTML document."""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title>{title}</title>
    <style>
        html {{
            overflow-x: hidden;
            width: 100%;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background-color: #faf9f5;
            transition: all 0.3s ease;
            box-sizing: border-box;
            overflow-x: hidden;
            width: 100%;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        * {{
            box-sizing: border-box;
            max-width: 100%;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 15px;
                max-width: 100vw;
            }}
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}
        h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
        h3 {{ font-size: 1.25em; }}
        code {{
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 85%;
        }}
        pre {{
            background-color: #f6f8fa;
            padding: 16px;
            overflow: auto;
            border-radius: 6px;
            max-width: 100%;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
        }}
        ul, ol {{
            padding-left: 2em;
        }}
        li {{
            margin-bottom: 0.25em;
        }}
        p {{
            margin-bottom: 16px;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}

        /* 悬浮按钮样式 */
        .float-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background-color: #0366d6;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            transition: all 0.3s ease;
        }}
        .float-btn:hover {{
            background-color: #0256c7;
            transform: scale(1.1);
        }}
        .float-btn svg {{
            width: 28px;
            height: 28px;
            fill: white;
        }}

        /* 设置面板样式 */
        .settings-panel {{
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 320px;
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(5px);
            -webkit-backdrop-filter: blur(5px);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            border: 1px solid rgba(200, 200, 200, 0.5);
            padding: 24px;
            z-index: 999;
            display: none;
        }}
        .settings-panel.active {{
            display: block;
            animation: slideIn 0.3s ease;
        }}
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        .settings-panel h3 {{
            margin: 0 0 20px 0;
            font-size: 18px;
            color: #333;
        }}
        .setting-item {{
            margin-bottom: 20px;
        }}
        .setting-item label {{
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }}
        .setting-item input[type="range"] {{
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #e1e4e8;
            outline: none;
            -webkit-appearance: none;
        }}
        .setting-item input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #0366d6;
            cursor: pointer;
        }}
        .setting-item input[type="range"]::-moz-range-thumb {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #0366d6;
            cursor: pointer;
            border: none;
        }}
        .setting-value {{
            display: inline-block;
            margin-left: 8px;
            font-size: 14px;
            color: #0366d6;
            font-weight: 600;
            min-width: 50px;
        }}
        .reset-btn {{
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            background-color: #f6f8fa;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            color: #333;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .reset-btn:hover {{
            background-color: #e1e4e8;
        }}
    </style>
</head>
<body>
{body_content}

<!-- 悬浮按钮 -->
<div class="float-btn" onclick="toggleSettings()">
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 15.5A3.5 3.5 0 0 1 8.5 12 3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5 3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97 0-.33-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.31-.61-.22l-2.49 1c-.52-.39-1.06-.73-1.69-.98l-.37-2.65A.506.506 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.37 2.65c-.63.25-1.17.59-1.69.98l-2.49-1c-.22-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64L4.57 11c-.04.34-.07.67-.07 1 0 .33.03.65.07.97l-2.11 1.66c-.19.15-.25.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1.01c.52.4 1.06.74 1.69.99l.37 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.37-2.65c.63-.26 1.17-.59 1.69-.99l2.49 1.01c.22.08.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.66z"/>
    </svg>
</div>

<!-- 设置面板 -->
<div class="settings-panel" id="settingsPanel">
    <h3>阅读设置</h3>

    <div class="setting-item">
        <label>
            字体大小
            <span class="setting-value" id="fontSizeValue">16px</span>
        </label>
        <input type="range" id="fontSize" min="12" max="24" value="16" step="1">
    </div>

    <div class="setting-item">
        <label>
            行间距
            <span class="setting-value" id="lineHeightValue">1.6</span>
        </label>
        <input type="range" id="lineHeight" min="1.0" max="3.0" value="1.6" step="0.1">
    </div>

    <div class="setting-item">
        <label>
            字间距
            <span class="setting-value" id="letterSpacingValue">0px</span>
        </label>
        <input type="range" id="letterSpacing" min="-1" max="10" value="0" step="0.5">
    </div>

    <button class="reset-btn" onclick="resetSettings()">重置默认</button>
</div>

<script>
    // 从localStorage加载设置
    function loadSettings() {{
        const fontSize = localStorage.getItem('fontSize') || '16';
        const lineHeight = localStorage.getItem('lineHeight') || '1.6';
        const letterSpacing = localStorage.getItem('letterSpacing') || '0';

        document.getElementById('fontSize').value = fontSize;
        document.getElementById('lineHeight').value = lineHeight;
        document.getElementById('letterSpacing').value = letterSpacing;

        applySettings(fontSize, lineHeight, letterSpacing);
    }}

    // 应用设置
    function applySettings(fontSize, lineHeight, letterSpacing) {{
        document.body.style.fontSize = fontSize + 'px';
        document.body.style.lineHeight = lineHeight;

        // 移除之前的样式和包装
        document.querySelectorAll('.cn-char').forEach(el => {{
            const parent = el.parentNode;
            parent.replaceChild(document.createTextNode(el.textContent), el);
            parent.normalize();
        }});

        // 如果字间距不为0，则包装中文字符
        if (letterSpacing != 0) {{
            wrapChineseCharacters(letterSpacing);
        }}

        document.getElementById('fontSizeValue').textContent = fontSize + 'px';
        document.getElementById('lineHeightValue').textContent = lineHeight;
        document.getElementById('letterSpacingValue').textContent = letterSpacing + 'px';
    }}

    // 包装中文字符以应用字间距
    function wrapChineseCharacters(spacing) {{
        // 移除之前的动态样式
        const oldStyle = document.getElementById('dynamic-letter-spacing');
        if (oldStyle) {{
            oldStyle.remove();
        }}

        // 创建新样式
        const style = document.createElement('style');
        style.id = 'dynamic-letter-spacing';
        style.textContent = `.cn-char {{ letter-spacing: ${{spacing}}px; }}`;
        document.head.appendChild(style);

        // 遍历所有文本节点
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {{
                acceptNode: function(node) {{
                    // 跳过script、style、code、pre标签
                    const parent = node.parentElement;
                    if (!parent || parent.classList.contains('cn-char') ||
                        ['SCRIPT', 'STYLE', 'CODE', 'PRE'].includes(parent.tagName)) {{
                        return NodeFilter.FILTER_REJECT;
                    }}
                    // 只处理包含中文的文本节点
                    if (/[\u4e00-\u9fa5]/.test(node.textContent)) {{
                        return NodeFilter.FILTER_ACCEPT;
                    }}
                    return NodeFilter.FILTER_REJECT;
                }}
            }}
        );

        const nodesToProcess = [];
        let node;
        while (node = walker.nextNode()) {{
            nodesToProcess.push(node);
        }}

        nodesToProcess.forEach(textNode => {{
            const fragment = document.createDocumentFragment();
            const text = textNode.textContent;
            let lastIndex = 0;

            // 正则匹配中文字符
            const regex = /[\u4e00-\u9fa5]/g;
            let match;

            while ((match = regex.exec(text)) !== null) {{
                // 添加中文之前的文本
                if (match.index > lastIndex) {{
                    fragment.appendChild(document.createTextNode(text.substring(lastIndex, match.index)));
                }}

                // 包装中文字符
                const span = document.createElement('span');
                span.className = 'cn-char';
                span.textContent = match[0];
                fragment.appendChild(span);

                lastIndex = match.index + 1;
            }}

            // 添加剩余文本
            if (lastIndex < text.length) {{
                fragment.appendChild(document.createTextNode(text.substring(lastIndex)));
            }}

            // 替换原文本节点
            textNode.parentNode.replaceChild(fragment, textNode);
        }});
    }}

    // 切换设置面板
    function toggleSettings() {{
        const panel = document.getElementById('settingsPanel');
        panel.classList.toggle('active');
    }}

    // 重置设置
    function resetSettings() {{
        localStorage.removeItem('fontSize');
        localStorage.removeItem('lineHeight');
        localStorage.removeItem('letterSpacing');
        loadSettings();
    }}

    // 监听滑块变化
    document.getElementById('fontSize').addEventListener('input', function(e) {{
        const value = e.target.value;
        localStorage.setItem('fontSize', value);
        applySettings(value, document.getElementById('lineHeight').value, document.getElementById('letterSpacing').value);
    }});

    document.getElementById('lineHeight').addEventListener('input', function(e) {{
        const value = e.target.value;
        localStorage.setItem('lineHeight', value);
        applySettings(document.getElementById('fontSize').value, value, document.getElementById('letterSpacing').value);
    }});

    document.getElementById('letterSpacing').addEventListener('input', function(e) {{
        const value = e.target.value;
        localStorage.setItem('letterSpacing', value);
        applySettings(document.getElementById('fontSize').value, document.getElementById('lineHeight').value, value);
    }});

    // 点击面板外部关闭
    document.addEventListener('click', function(e) {{
        const panel = document.getElementById('settingsPanel');
        const btn = document.querySelector('.float-btn');
        if (!panel.contains(e.target) && !btn.contains(e.target)) {{
            panel.classList.remove('active');
        }}
    }});

    // 页面加载时应用设置
    loadSettings();
</script>
</body>
</html>"""


def process_markdown_file(md_file_path):
    """Convert a single Markdown file to HTML."""
    try:
        md_path = Path(md_file_path)

        if not md_path.exists():
            print(f"Error: File '{md_file_path}' not found.")
            return False

        # Read Markdown file
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convert to HTML
        html_body = convert_md_to_html(md_content)

        # Create full HTML document
        title = md_path.stem
        full_html = create_html_template(title, html_body)

        # Write HTML file
        html_path = md_path.with_suffix('.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

        print(f"✓ Converted: {md_path.name} -> {html_path.name}")
        return True

    except Exception as e:
        print(f"✗ Error processing '{md_file_path}': {str(e)}")
        return False


def main():
    # Check for recursive flag
    recursive = False
    if len(sys.argv) > 1 and sys.argv[1] == '-r':
        recursive = True

    # Scan for markdown files
    files_to_process = []
    current_dir = Path('.')

    if recursive:
        # Recursively find all .md files in current directory and subdirectories
        print("Scanning current directory and subdirectories for Markdown files...")
        files_to_process = list(current_dir.rglob('*.md'))
    else:
        # Find .md files only in current directory
        print("Scanning current directory for Markdown files...")
        files_to_process = list(current_dir.glob('*.md'))

    # Convert Path objects to strings
    files_to_process = [str(f) for f in files_to_process]

    if not files_to_process:
        print("No Markdown files found.")
        sys.exit(0)

    print(f"Found {len(files_to_process)} Markdown file(s).\n")

    # Process each file
    success_count = 0
    for file_path in files_to_process:
        if process_markdown_file(file_path):
            success_count += 1

    print(f"\nProcessed {success_count}/{len(files_to_process)} files successfully.")


if __name__ == '__main__':
    main()
