import os
import json
import requests
from PIL import Image
from io import BytesIO

# Configuration
INPUT_FILE = 'stories.json'
OUTPUT_FILE = 'stories_updated.json'
BASE_ASSETS_DIR = 'assets'
GITHUB_BASE_URL = "https://convoluteai.github.io/theenchantingtales-public/assets"

def process_image(url, story_id, img_index):
    # Create directory for the story
    story_dir = os.path.join(BASE_ASSETS_DIR, str(story_id))
    os.makedirs(story_dir, exist_ok=True)
    
    file_name = f"{img_index}.webp"
    file_path = os.path.join(story_dir, file_name)
    
    try:
        # Download image
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Convert to WebP and optimize
        img = Image.open(BytesIO(response.content))
        # Ensure it is in RGB mode (required for JPEG/WebP conversion)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # Save as WebP: quality 70 is usually sweet spot for size/quality
        img.save(file_path, "WEBP", quality=70, method=6)
        
        # Return new GitHub URL
        return f"{GITHUB_BASE_URL}/{story_id}/{file_name}"
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return url # Keep original if it fails

# Load existing JSON
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    stories = json.load(f)

for story in stories:
    story_id = story['id']
    print(f"Processing Story {story_id}: {story['title']}")
    
    # 1. Update main thumbnail image
    if 'image' in story and 'uri' in story['image']:
        new_url = process_image(story['image']['uri'], story_id, "thumb")
        story['image']['uri'] = new_url
        
    # 2. Update images inside the content array
    img_counter = 1
    for item in story.get('content', []):
        if item['type'] == 'image' and 'source' in item:
            new_url = process_image(item['source']['uri'], story_id, img_counter)
            item['source']['uri'] = new_url
            img_counter += 1

# Save updated JSON
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(stories, f, indent=4)

print(f"\nMigration complete! Updated JSON saved to {OUTPUT_FILE}")