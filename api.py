from flask import Flask, request, jsonify
import re
import requests
import time
import webserver

app = Flask(__name__)

key_regex = r'let content = \("([^"]+)"\);'

def fetch(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch URL: {url}. Error: {e}")

def bypass_link(url):
    try:
        hwid = url.split("HWID=")[-1]
        if not hwid:
            raise Exception("Invalid HWID in URL")

        start_time = time.time()
        endpoints = [
            {
                "url": f"https://flux.li/android/external/start.php?HWID={hwid}",
                "referer": ""
            },
            {
                "url": "https://flux.li/android/external/check1.php?hash={hash}",
                "referer": "https://linkvertise.com"
            },
            {
                "url": "https://flux.li/android/external/main.php?hash={hash}",
                "referer": "https://linkvertise.com"
            }
        ]

        for endpoint in endpoints:
            url = endpoint["url"]
            referer = endpoint["referer"]
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'close',
                'Referer': referer,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x66) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            response_text = fetch(url, headers)
            if endpoint == endpoints[-1]:
                match = re.search(key_regex, response_text)
                if match:
                    end_time = time.time()
                    time_taken = end_time - start_time
                    return match.group(1), time_taken
                else:
                    raise Exception("Failed to find content key")
    except Exception as e:
        raise Exception(f"Failed to bypass link. Error: {e}")

# Modify the home endpoint to accept URL parameter and bypass
@app.route("/")
def home():
    url = request.args.get("url")  # Get 'url' parameter from the query string
    if url:
        if url.startswith("https://flux.li/android/external/start.php?HWID="):
            try:
                content, time_taken = bypass_link(url)
                return jsonify({"key": content, "time_taken": time_taken, "credit": "Hydra"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"message": "Please Enter a Valid Fluxus Link!"})
    else:
        return jsonify({"message": "No URL provided. Please provide a Fluxus link using ?url=<your_link>"})

@app.route("/api/fluxus")
def bypass():
    url = request.args.get("url")
    if url.startswith("https://flux.li/android/external/start.php?HWID="):
        try:
            content, time_taken = bypass_link(url)
            return jsonify({"key": content, "time_taken": time_taken, "credit": "Hydra"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"message": "Please Enter Fluxus Link!"})

webserver.keep_alive()