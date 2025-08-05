import re
import pandas as pd

# Load the uploaded CSV file
file_path = 'bebop_videos_filtered.csv'
jazz_data = pd.read_csv(file_path)

# Function to extract the year from the Title or Description
def extract_year(row):
    # Look for a year pattern in the Title or Description
    title_year = re.search(r'\b(19[0-5][0-9])\b', row['Title'])
    desc_year = re.search(r'\b(19[0-5][0-9])\b', str(row['Description']))
    
    # Return the first found year, prioritizing Title
    if title_year:
        return int(title_year.group(1))
    elif desc_year:
        return int(desc_year.group(1))
    return None

# Apply the function to extract years
jazz_data['Year'] = jazz_data.apply(extract_year, axis=1)

# Filter for videos before 1955 and drop duplicates based on the URL
filtered_jazz_data = jazz_data[(jazz_data['Year'] < 1955) & jazz_data['Year'].notna()]
filtered_jazz_data = filtered_jazz_data.drop_duplicates(subset='Video URL')

# Save the filtered data to a new file for review
output_path = '/Users/leomckenna/Desktop/Music Research/filtered_jazz_videos.csv'
filtered_jazz_data.to_csv(output_path, index=False)