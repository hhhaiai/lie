import json
import time
from pathlib import Path
from curl_cffi.requests import Session, RequestsError

# --- Configuration ---
AUTH_CACHE_FILE = Path("auth_imagelabs.json")
TXT2IMG_URL = "https://editor.imagelabs.net/txt2img"
PROGRESS_URL = "https://editor.imagelabs.net/progress"
POLL_INTERVAL_SECONDS = 3
MAX_POLL_ATTEMPTS = 100

def get_auth_args() -> dict | None:
    """
    Loads authentication arguments from a cache file, with detailed instructions.
    """
    if not AUTH_CACHE_FILE.exists():
        print(f"Authentication file '{AUTH_CACHE_FILE}' not found.")
        print("\n--- How to Create 'auth_imagelabs.json' ---")
        # ... (Instructions are unchanged) ...
        print("""
{
    "headers": {
        "user-agent": "COPY_USER_AGENT_HERE_FROM_CURL"
    },
    "cookies": {
        "__ga": "COPY_GA_COOKIE_VALUE_HERE",
        "session": "COPY_SESSION_COOKIE_VALUE_HERE",
        "cf_clearance": "COPY_CF_CLEARANCE_COOKIE_VALUE_HERE"
    }
}
""")
        return None
    
    try:
        with AUTH_CACHE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading auth file '{AUTH_CACHE_FILE}': {e}")
        return None

def save_auth_args(auth_args: dict, session: Session):
    """Saves updated cookies from the session back to the auth file."""
    updated_cookies = session.cookies.get_dict()
    if not updated_cookies:
        return
        
    auth_args['cookies'] = updated_cookies
    try:
        with AUTH_CACHE_FILE.open("w", encoding="utf-8") as f:
            json.dump(auth_args, f, indent=4)
        print("\nℹ️  Authentication cookies have been updated and saved.")
    except IOError as e:
        print(f"\n⚠️ Error saving updated auth file: {e}")

def generate_image(
    prompt: str,
    output_filename: str = "output.jpg",
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 768
) -> bool:
    auth_args = get_auth_args()
    if not auth_args:
        return False

    # Use curl_cffi Session, impersonating a Chrome browser
    session = Session(impersonate="chrome110")
    session.cookies.update(auth_args.get("cookies", {}))

    base_headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'content-type': 'application/json; charset=UTF-8',
        'origin': 'https://editor.imagelabs.net',
        'referer': 'https://editor.imagelabs.net/',
        'x-requested-with': 'XMLHttpRequest',
        **auth_args.get("headers", {})
    }
    session.headers.update(base_headers)
    
    initial_payload = {
        "prompt": prompt, "seed": str(int(time.time())), "subseed": str(int(time.time() * 1000)),
        "attention": 0, "width": width, "height": height, "tiling": False,
        "negative_prompt": negative_prompt, "reference_image": "", "reference_image_type": None,
        "reference_strength": 30
    }
    
    try:
        print("🚀 Submitting image generation task...")
        response = session.post(TXT2IMG_URL, json=initial_payload, timeout=60)
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data.get("task_id")

        if not task_id:
            print(f"❌ Failed to get task_id. Response: {task_data}")
            return False
        
        print(f"✅ Task submitted successfully. Task ID: {task_id}")
        print("⏳ Polling for task progress...")

        for attempt in range(MAX_POLL_ATTEMPTS):
            progress_payload = {"task_id": task_id}
            progress_response = session.post(PROGRESS_URL, json=progress_payload, timeout=60)
            progress_response.raise_for_status()
            progress_data = progress_response.json()
            
            status = progress_data.get("status", "Unknown")
            progress = progress_data.get("progress", 0) * 100
            final_image_url = progress_data.get("final_image_url")

            print(f"\r   Attempt {attempt + 1}/{MAX_POLL_ATTEMPTS}: Status: '{status}', Progress: {progress:.1f}%", end="")

            if final_image_url:
                print("\n✅ Image generation complete!")
                print(f"⬇️ Downloading final image from: {final_image_url}")
                # Use a standard requests session for the final download if issues arise
                image_response = Session().get(final_image_url, timeout=120)
                image_response.raise_for_status()
                
                Path("imagelabs_output").mkdir(exist_ok=True)
                output_path = Path("imagelabs_output") / output_filename
                with open(output_path, 'wb') as f:
                    f.write(image_response.content)
                print(f"🖼️  Image successfully saved to '{output_path}'")
                return True

            time.sleep(POLL_INTERVAL_SECONDS)
        
        print("\n❌ Max poll attempts reached. Task did not complete in time.")
        return False

    except RequestsError as e:
        print(f"\nAn error occurred during the request: {e}")
        return False
    except (json.JSONDecodeError, KeyError) as e:
        print(f"\nFailed to parse server response: {e}")
        return False
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        return False
    finally:
        save_auth_args(auth_args, session)

if __name__ == "__main__":
    user_prompt = "A beautiful woman, detailed face, cinematic lighting, masterpiece"
    safe_prompt_name = "".join(c for c in user_prompt if c.isalnum() or c in " _-").rstrip()[:50]
    filename = f"{safe_prompt_name}_{int(time.time())}.jpg"
    generate_image(user_prompt, output_filename=filename) 