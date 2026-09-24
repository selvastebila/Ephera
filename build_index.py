import os

with open('src/lib/audio.js', 'r', encoding='utf-8') as f:
    audio_js = f.read()

with open('src/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

with open('src/styles/globals.css', 'r', encoding='utf-8') as f:
    globals_css = f.read()

html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WoodSafe Guardian - AI Woodworking Safety Monitoring System</title>
    <meta name="description" content="AI-powered safety monitoring system for woodworking environments. Real-time T300 Table Saw distance tracking, auto-shutdown, hand speed monitoring, and multi-machine safety control.">
    <link rel="shortcut icon" href="https://fav.farm/🛡️" type="image/x-icon">

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">

    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />

    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwindcss = {{
        darkMode: 'class',
        theme: {{
          extend: {{
            colors: {{
              industrial: {{
                950: '#090d16',
                900: '#0f172a',
                800: '#1e293b'
              }}
            }}
          }}
        }}
      }}
    </script>

    <!-- Custom Global Stylesheet -->
    <style>
{globals_css}
    </style>

    <!-- React 18 & Babel Standalone -->
    <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

    <!-- Web Audio Synthesizer Library -->
    <script>
{audio_js}
    </script>
</head>
<body class="bg-slate-950 text-slate-100 antialiased selection:bg-amber-500 selection:text-slate-950">

    <!-- Root App Container -->
    <div id="root"></div>

    <!-- React Application Code -->
    <script type="text/babel">
{app_js}
    </script>

</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Successfully created standalone index.html with inlined React & Web Audio code!')
