import os
import subprocess
import shutil
import tempfile

def create_desktop_entry():
    # Define the desktop file path
    desktop_file_path = os.path.expanduser("~/.local/share/applications/validapp.desktop")

    # Check if the desktop entry already exists
    if os.path.exists(desktop_file_path):
        print("Desktop entry already exists. Skipping setup.")
        return  # Exit the function if the desktop entry exists

    # Define the desktop entry content
    desktop_entry = (
        "[Desktop Entry]\n"
        "Name=ValiDapp\n"
        "Comment=Ethereum Validator Management App\n"
        "Exec=/usr/bin/validapp %U\n"
        "Icon=/usr/share/icons/hicolor/256x256/apps/validapp.png\n"
        "Terminal=true\n"
        "Type=Application\n"
        "Categories=Utility;Application;\n"
    )

    # Create the .desktop file with proper formatting
    with open(desktop_file_path, 'w') as desktop_file:
        desktop_file.write(desktop_entry)

    # Make the .desktop file executable
    os.chmod(desktop_file_path, 0o755)

    # Copy the icon to a temporary location first
    app_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_source_path = os.path.join(app_root_dir, "app/assets/logo.png")
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp_icon:
        try:
            shutil.copyfile(icon_source_path, tmp_icon.name)
            print(f"Icon temporarily copied to {tmp_icon.name}")

            # Use sudo to move the icon to the system directory
            icon_target_path = "/usr/share/icons/hicolor/256x256/apps/validapp.png"
            subprocess.check_call(['sudo', 'mv', tmp_icon.name, icon_target_path])
            print(f"Icon moved to {icon_target_path}")
        
        except Exception as e:
            print(f"Failed to copy or move icon: {e}")
        
        finally:
            # Clean up the temporary file if it still exists
            if os.path.exists(tmp_icon.name):
                os.remove(tmp_icon.name)

    # Refresh the desktop database
    subprocess.call(['update-desktop-database', os.path.expanduser("~/.local/share/applications")])

if __name__ == "__main__":
    create_desktop_entry()
