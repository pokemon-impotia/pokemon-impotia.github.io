import os
import shutil
import json
import csv
from PIL import Image

# --- Configuration ---
FANGAME_ROOT_FOLDER = r'C:\Users\fuyutaa\Documents\GitHub\POKEMON-IMPOTIA\IMPOTIA RMXP'
WEB_PROJECT_ROOT_FOLDER = r'C:\xampp\htdocs\pokedex_web'

# Output directory within the web project for processed assets
OUTPUT_DATA_FOLDER = os.path.join(WEB_PROJECT_ROOT_FOLDER, 'data')

# Source paths relative to FANGAME_ROOT_FOLDER
PSDK_NATIONAL_DEX_PATH = os.path.join(FANGAME_ROOT_FOLDER, r'Data\Studio\dex\national.json')
PSDK_CSV_DIALOGS_PATH = os.path.join(FANGAME_ROOT_FOLDER, r'Data\Text\Dialogs')
PSDK_POKEMON_JSONS_FOLDER = os.path.join(FANGAME_ROOT_FOLDER, r'Data\Studio\pokemon')
PSDK_MOVES_JSONS_FOLDER = os.path.join(FANGAME_ROOT_FOLDER, r'Data\Studio\moves')
PSDK_ABILITIES_JSONS_FOLDER = os.path.join(FANGAME_ROOT_FOLDER, r'Data\Studio\abilities')
PSDK_POKEFRONT_SPRITES_FOLDER = os.path.join(FANGAME_ROOT_FOLDER, r'graphics\pokedex\pokefront')

# Destination paths relative to WEB_PROJECT_ROOT_FOLDER (or OUTPUT_DATA_FOLDER)
WEB_NATIONAL_DEX_PATH = os.path.join(OUTPUT_DATA_FOLDER, 'national.json')
WEB_TRANSLATIONS_FOLDER = os.path.join(OUTPUT_DATA_FOLDER, 'translations')
WEB_POKEMON_CONSOLIDATED_FOLDER = os.path.join(OUTPUT_DATA_FOLDER, 'pokemon_consolidated')
WEB_POKEFRONT_UPSCALED_FOLDER = os.path.join(OUTPUT_DATA_FOLDER, 'pokefront')

# CSV File IDs and their roles
CSV_ABILITIES_NAMES_ID = '100004'
CSV_ABILITIES_DESCRIPTIONS_ID = '100005'
CSV_MOVES_NAMES_ID = '100006'

# Language mapping for CSVs
LANGUAGES = ['en', 'fr', 'it', 'de', 'es', 'ko']

# --- Helper Functions ---

def ensure_directory_exists(path):
    """Ensures that a directory exists, creating it if necessary."""
    os.makedirs(path, exist_ok=True)

def load_csv_as_dict(file_path):
    """Loads a CSV file into a dictionary where row index (from 1) maps to a list of column values."""
    data = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            data[i] = row
    return data

def get_translated_text_from_csv(csv_data, text_id, lang_index):
    """Retrieves translated text from loaded CSV data."""
    if text_id is None:
        return "Unknown"
    row = csv_data.get(text_id)
    if row and len(row) > lang_index:
        return row[lang_index].strip('"')
    return "Translation Not Found"

# --- Main Script Logic ---

def run_setup():
    print("Starting Pokédex Web Setup Script...")

    # 1. Prepare output directories
    ensure_directory_exists(OUTPUT_DATA_FOLDER)
    ensure_directory_exists(WEB_TRANSLATIONS_FOLDER)
    ensure_directory_exists(WEB_POKEMON_CONSOLIDATED_FOLDER)
    ensure_directory_exists(WEB_POKEFRONT_UPSCALED_FOLDER)

    # 2. Copy national.json
    print(f"Copying national.json...")
    shutil.copy(PSDK_NATIONAL_DEX_PATH, WEB_NATIONAL_DEX_PATH)

    # 3. Load CSV data for translations
    print("Loading CSV translation files...")
    abilities_names_csv = load_csv_as_dict(os.path.join(PSDK_CSV_DIALOGS_PATH, f'{CSV_ABILITIES_NAMES_ID}.csv'))
    abilities_descriptions_csv = load_csv_as_dict(os.path.join(PSDK_CSV_DIALOGS_PATH, f'{CSV_ABILITIES_DESCRIPTIONS_ID}.csv'))
    moves_names_csv = load_csv_as_dict(os.path.join(PSDK_CSV_DIALOGS_PATH, f'{CSV_MOVES_NAMES_ID}.csv'))

    # 4. Upscale and copy Pokémon front sprites
    print("Upscaling and copying Pokémon front sprites...")
    for filename in os.listdir(PSDK_POKEFRONT_SPRITES_FOLDER):
        if filename.endswith('.png'):
            src_path = os.path.join(PSDK_POKEFRONT_SPRITES_FOLDER, filename)
            dest_path = os.path.join(WEB_POKEFRONT_UPSCALED_FOLDER, filename.lower())
            try:
                with Image.open(src_path) as img:
                    new_size = (img.width * 4, img.height * 4)
                    upscaled_img = img.resize(new_size, Image.Resampling.NEAREST)
                    upscaled_img.save(dest_path)
            except Exception as e:
                print(f"ERROR: Failed to process sprite {filename}: {e}")

    # 5. Process national.json to consolidate Pokémon data
    print("\n=== Starting Pokémon Consolidation ===")
    try:
        with open(WEB_NATIONAL_DEX_PATH, 'r', encoding='utf-8') as f:
            national_dex_data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: national.json not found at {WEB_NATIONAL_DEX_PATH}")
        return

    pokemon_symbols_to_process = [creature['dbSymbol'] for creature in national_dex_data['creatures']]
    print(f"Found {len(pokemon_symbols_to_process)} Pokémon in national.json")

    success_count = 0
    error_count = 0

    for pokemon_symbol in pokemon_symbols_to_process:
        try:
            # Load base Pokémon JSON
            pokemon_json_path = os.path.join(PSDK_POKEMON_JSONS_FOLDER, f'{pokemon_symbol}.json')
            
            if not os.path.exists(pokemon_json_path):
                print(f"ERROR: {pokemon_symbol}.json NOT FOUND at {pokemon_json_path}")
                error_count += 1
                continue
                
            with open(pokemon_json_path, 'r', encoding='utf-8') as f:
                pokemon_data = json.load(f)

            if not pokemon_data.get('forms'):
                print(f"ERROR: {pokemon_symbol} has no forms in JSON")
                error_count += 1
                continue
            
            form = pokemon_data['forms'][0]

            # Consolidate Abilities
            consolidated_abilities = []
            processed_ability_symbols = set()
            for ability_symbol in form.get('abilities', []):
                if ability_symbol in processed_ability_symbols:
                    continue
                processed_ability_symbols.add(ability_symbol)

                ability_json_path = os.path.join(PSDK_ABILITIES_JSONS_FOLDER, f'{ability_symbol}.json')
                try:
                    with open(ability_json_path, 'r', encoding='utf-8') as f:
                        ability_details = json.load(f)
                    
                    text_id = ability_details.get('textId')
                    
                    translated_names = {}
                    translated_descriptions = {}
                    for i, lang in enumerate(LANGUAGES):
                        translated_names[lang] = get_translated_text_from_csv(abilities_names_csv, text_id, i)
                        translated_descriptions[lang] = get_translated_text_from_csv(abilities_descriptions_csv, text_id, i)
                    
                    consolidated_abilities.append({
                        'symbol': ability_symbol,
                        'textId': text_id,
                        'names': translated_names,
                        'descriptions': translated_descriptions
                    })
                except FileNotFoundError:
                    print(f"ERROR: Ability {ability_symbol}.json not found for {pokemon_symbol}")
                    consolidated_abilities.append({
                        'symbol': ability_symbol,
                        'names': {'en': ability_symbol},
                        'descriptions': {'en': 'Description not found.'}
                    })
                except Exception as e:
                    print(f"ERROR: Failed to process ability {ability_symbol} for {pokemon_symbol}: {e}")
                    consolidated_abilities.append({
                        'symbol': ability_symbol,
                        'names': {'en': ability_symbol},
                        'descriptions': {'en': 'Error loading description.'}
                    })
            form['abilities_data'] = consolidated_abilities

            # Consolidate Moves
            consolidated_moves = []
            processed_move_symbols = set()
            for move_entry in form.get('moveSet', []):
                move_symbol = move_entry.get('move')
                if not move_symbol or move_symbol in processed_move_symbols:
                    continue
                processed_move_symbols.add(move_symbol)

                move_json_path = os.path.join(PSDK_MOVES_JSONS_FOLDER, f'{move_symbol}.json')
                try:
                    with open(move_json_path, 'r', encoding='utf-8') as f:
                        move_details = json.load(f)
                    
                    move_id = move_details.get('id')
                    
                    translated_names = {}
                    for i, lang in enumerate(LANGUAGES):
                        translated_names[lang] = get_translated_text_from_csv(moves_names_csv, move_id, i)
                    
                    consolidated_moves.append({
                        'symbol': move_symbol,
                        'id': move_id,
                        'klass': move_entry.get('klass'),
                        'level': move_entry.get('level'),
                        'names': translated_names,
                        'category': move_details.get('category'),
                        'type': move_details.get('type'),
                        'pp': move_details.get('pp'),
                        'power': move_details.get('power'),
                        'accuracy': move_details.get('accuracy')
                    })
                except FileNotFoundError:
                    print(f"ERROR: Move {move_symbol}.json not found for {pokemon_symbol}")
                    consolidated_moves.append({
                        'symbol': move_symbol,
                        'names': {'en': move_symbol},
                        'category': 'unknown', 'type': 'unknown', 'pp': 0, 'power': 0, 'accuracy': 0
                    })
                except Exception as e:
                    print(f"ERROR: Failed to process move {move_symbol} for {pokemon_symbol}: {e}")
                    consolidated_moves.append({
                        'symbol': move_symbol,
                        'names': {'en': move_symbol},
                        'category': 'unknown', 'type': 'unknown', 'pp': 0, 'power': 0, 'accuracy': 0
                    })
            form['moves_data'] = consolidated_moves

            # Save consolidated Pokémon JSON
            output_pokemon_path = os.path.join(WEB_POKEMON_CONSOLIDATED_FOLDER, f'{pokemon_symbol}.json')
            with open(output_pokemon_path, 'w', encoding='utf-8') as f:
                json.dump(pokemon_data, f, indent=2, ensure_ascii=False)
            success_count += 1

        except FileNotFoundError:
            print(f"ERROR: Pokémon JSON not found for {pokemon_symbol}")
            error_count += 1
        except Exception as e:
            print(f"ERROR: Unexpected error processing {pokemon_symbol}: {e}")
            error_count += 1

    print(f"\n=== Consolidation Complete ===")
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")

if __name__ == '__main__':
    print("This script prepares PSDK assets for the web Pokédex.")
    print("Please ensure you have Pillow (pip install Pillow) installed.")
    print("\n--- IMPORTANT ---")
    print("BEFORE RUNNING, EDIT THE 'FANGAME_ROOT_FOLDER' AND 'WEB_PROJECT_ROOT_FOLDER' VARIABLES")
    print(f"IN THIS SCRIPT ({os.path.basename(__file__)}) TO YOUR ACTUAL PATHS.")
    print("-----------------\n")

    confirmation = input("Do you want to run the setup script now? (yes/no): ").lower()
    if confirmation == 'yes':
        run_setup()
    else:
        print("Setup script aborted by user.")