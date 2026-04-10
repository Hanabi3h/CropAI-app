"""
Find and display all CSV files in the project
"""
import os

print("=" * 60)
print("SEARCHING FOR CSV FILES")
print("=" * 60)

# Start from current directory
root_dir = os.getcwd()
print(f"Searching in: {root_dir}\n")

csv_files = []

# Walk through all directories
for foldername, subfolders, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith('.csv'):
            full_path = os.path.join(foldername, filename)
            csv_files.append(full_path)
            print(f"✅ Found: {full_path}")

if not csv_files:
    print("❌ No CSV files found!")
    print("\nCurrent directory contents:")
    for item in os.listdir('.'):
        print(f"  - {item}")
else:
    print(f"\n📊 Found {len(csv_files)} CSV file(s)")
    print("\n💡 To fix: Add this to your data_loader.py:")
    print("\nAdd this path to the default_paths list:")
    for csv_file in csv_files:
        relative_path = os.path.relpath(csv_file, root_dir)
        print(f"    '{relative_path}',")