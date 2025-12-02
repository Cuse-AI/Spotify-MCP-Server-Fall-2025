"""Quick script to check if a Spotify ID matches the intended song"""

# The correct Spotify ID for "IDK You Yet" by Alexander 23 should be:
# spotify:track:5dQKvjUfif80t7uJHjORXB

current_id = "0j1Ia2lQWrcXrQZI4AdJlk"
correct_id = "5dQKvjUfif80t7uJHjORXB"

print(f"Current ID in tapestry: {current_id}")
print(f"Correct ID for 'IDK You Yet': {correct_id}")
print(f"\nIDs match: {current_id == correct_id}")

if current_id != correct_id:
    print(f"\nThe current ID {current_id} is WRONG")
    print(f"It should be: {correct_id}")
