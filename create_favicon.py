#!/usr/bin/env python3
"""
Create favicon and app icons from the transparent logo.
"""

from PIL import Image
import os

def create_favicon_and_icons():
    """Create favicon and app icons in various sizes."""
    
    input_path = "stem/static/images/logo-tatlock-transparent.png"
    
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found!")
        return False
    
    try:
        # Open the transparent logo
        print(f"Opening {input_path}...")
        img = Image.open(input_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        print(f"Original size: {img.size}")
        
        # Create output directory for favicon
        favicon_dir = "stem/static/favicon"
        os.makedirs(favicon_dir, exist_ok=True)
        
        # Define icon sizes for different purposes
        icon_sizes = {
            # Favicon sizes
            'favicon.ico': [(16, 16), (32, 32), (48, 48)],  # Multi-size ICO
            'favicon-16x16.png': [(16, 16)],
            'favicon-32x32.png': [(32, 32)],
            'favicon-48x48.png': [(48, 48)],
            
            # Apple touch icons
            'apple-touch-icon.png': [(180, 180)],
            'apple-touch-icon-152x152.png': [(152, 152)],
            'apple-touch-icon-144x144.png': [(144, 144)],
            'apple-touch-icon-120x120.png': [(120, 120)],
            'apple-touch-icon-114x114.png': [(114, 114)],
            'apple-touch-icon-76x76.png': [(76, 76)],
            'apple-touch-icon-72x72.png': [(72, 72)],
            'apple-touch-icon-60x60.png': [(60, 60)],
            'apple-touch-icon-57x57.png': [(57, 57)],
            
            # Android/Chrome icons
            'android-chrome-192x192.png': [(192, 192)],
            'android-chrome-512x512.png': [(512, 512)],
            
            # Windows tiles
            'mstile-150x150.png': [(150, 150)],
            
            # General app icons
            'icon-192x192.png': [(192, 192)],
            'icon-512x512.png': [(512, 512)],
        }
        
        created_files = []
        
        for filename, sizes in icon_sizes.items():
            output_path = os.path.join(favicon_dir, filename)
            
            if filename == 'favicon.ico':
                # Create multi-size ICO file
                print(f"Creating {filename}...")
                images = []
                for size in sizes:
                    resized = img.resize(size, Image.Resampling.LANCZOS)
                    images.append(resized)
                
                # Save as ICO with multiple sizes
                images[0].save(output_path, format='ICO', sizes=[(size[0], size[1]) for size in sizes])
                created_files.append(output_path)
                
            else:
                # Create single-size PNG files
                size = sizes[0]
                print(f"Creating {filename} ({size[0]}x{size[1]})...")
                
                # Resize image
                resized = img.resize(size, Image.Resampling.LANCZOS)
                
                # Save as PNG
                resized.save(output_path, 'PNG', optimize=True)
                created_files.append(output_path)
        
        print(f"\n✅ Successfully created {len(created_files)} favicon/app icon files!")
        print("Files created in stem/static/favicon/")
        
        # List created files
        for filepath in created_files:
            filename = os.path.basename(filepath)
            print(f"  - {filename}")
        
        return True
        
    except Exception as e:
        print(f"Error creating favicon: {e}")
        return False

def create_web_manifest():
    """Create a web app manifest file."""
    
    manifest_content = '''{
  "name": "Tatlock",
  "short_name": "Tatlock",
  "description": "Brain-inspired conversational AI platform",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#000000",
  "icons": [
    {
      "src": "/static/favicon/android-chrome-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/favicon/android-chrome-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}'''
    
    manifest_path = "stem/static/manifest.json"
    
    try:
        with open(manifest_path, 'w') as f:
            f.write(manifest_content)
        
        print(f"✅ Created web app manifest: {manifest_path}")
        return True
        
    except Exception as e:
        print(f"Error creating manifest: {e}")
        return False

if __name__ == "__main__":
    print("=== Creating Favicon and App Icons ===")
    print()
    
    # Create favicon and app icons
    success1 = create_favicon_and_icons()
    
    print()
    
    # Create web app manifest
    success2 = create_web_manifest()
    
    print()
    if success1 and success2:
        print("🎉 Favicon and app icons created successfully!")
        print("Next step: Update your HTML templates to include the favicon links.")
    else:
        print("❌ Some files failed to create. Check the errors above.") 