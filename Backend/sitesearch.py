import webbrowser

def site_open(app_name):
    # Define paths for browsers
    brave_path = "/usr/bin/brave-browser %s"
    firefox_path = "/usr/bin/firefox %s"

    # Dictionary of popular apps/websites
    apps = {
        "whatsapp": ("https://web.whatsapp.com", firefox_path),
        "youtube": ("https://www.youtube.com", firefox_path),
        "google": ("https://www.google.com", firefox_path),
        "github": ("https://github.com", firefox_path),
        "reddit": ("https://www.reddit.com", firefox_path),
        "linkedin": ("https://www.linkedin.com", firefox_path),
        "twitter": ("https://twitter.com", firefox_path),
        "instagram": ("https://www.instagram.com", firefox_path)
    }

    # Get the URL and browser path
    url, browser_path = apps.get(app_name.lower(), (app_name, brave_path))

    # Open the website/application
    try:
        webbrowser.get(browser_path).open(url)
    except webbrowser.Error as e:
        print(f"An error occurred: {e}")

