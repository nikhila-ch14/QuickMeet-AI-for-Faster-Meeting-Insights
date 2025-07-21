import pdfkit
import platform
import os

# === Detect platform and set wkhtmltopdf path manually if needed ===

# Example default paths for common platforms
if platform.system() == "Windows":
    # Make sure wkhtmltopdf is installed at this path or update accordingly
    path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
elif platform.system() == "Darwin":  # macOS
    path_to_wkhtmltopdf = "/usr/local/bin/wkhtmltopdf"
else:  # Linux
    path_to_wkhtmltopdf = "/usr/bin/wkhtmltopdf"

# Create config object
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

def generate_pdf_from_files(summary_path='summary.txt', action_items_path='action_items.txt'):
    # Read from text files
    with open(summary_path, 'r', encoding='utf-8') as f:
        meeting_summary = f"<p>{f.read().replace('\n', '<br>')}</p>"

    with open(action_items_path, 'r', encoding='utf-8') as f:
        action_items = f.read().splitlines()
        action_items_html = "<ul>" + ''.join(f"<li>{item}</li>" for item in action_items) + "</ul>"

    # HTML template
    html_content = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Meeting Summary and Action Items</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            margin: 20px;
          }}
          h1, h2 {{
            color: #333;
          }}
          .section {{
            margin-bottom: 30px;
          }}
          ul {{
            list-style-type: disc;
            margin-left: 20px;
          }}
          li {{
            margin-bottom: 10px;
          }}
        </style>
      </head>
      <body>
        <h1>Meeting Summary</h1>
        <div class="section">{meeting_summary}</div>
        <h2>Action Items</h2>
        <div class="section">{action_items_html}</div>
      </body>
    </html>
    """

    # Generate PDF as bytes with configured path
    pdf_data = pdfkit.from_string(html_content, False, configuration=config)
    return pdf_data
