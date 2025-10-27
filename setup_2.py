import json
import os
import shutil
from pathlib import Path

# --- Configuration ---
FANGAME_ROOT_FOLDER = r'C:\Users\fuyutaa\Documents\GitHub\POKEMON-IMPOTIA\IMPOTIA RMXP'
WEB_PROJECT_ROOT_FOLDER = r'C:\xampp\htdocs\pokedex_web'

# Paths
PSDK_NATIONAL_DEX_PATH = os.path.join(FANGAME_ROOT_FOLDER, r'Data\Studio\dex\national.json')
OUTPUT_DATA_FOLDER = os.path.join(WEB_PROJECT_ROOT_FOLDER, 'data')
WEB_NATIONAL_DEX_PATH = os.path.join(OUTPUT_DATA_FOLDER, 'national.json')

def load_json(filepath):
    """Load and parse a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save data to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def process_pokemon_types():
    """
    Process all Pokémon from national.json and their individual files
    to generate a summary of types with counts and Pokémon lists.
    """
    # Copy national.json from Studio project
    print(f"Copying national.json from {PSDK_NATIONAL_DEX_PATH} to {WEB_NATIONAL_DEX_PATH}...")
    try:
        shutil.copy(PSDK_NATIONAL_DEX_PATH, WEB_NATIONAL_DEX_PATH)
        print("✓ national.json copied successfully")
    except FileNotFoundError:
        print(f"Error: {PSDK_NATIONAL_DEX_PATH} not found!")
        return
    except Exception as e:
        print(f"Error copying national.json: {e}")
        return
    
    # Load the national pokedex
    national_path = Path(WEB_NATIONAL_DEX_PATH)
    if not national_path.exists():
        print(f"Error: {national_path} not found!")
        return
    
    national_data = load_json(national_path)
    creatures = national_data.get('creatures', [])
    
    # Initialize types dictionary
    types_data = {}
    total_pokemon = 0
    pokemon_consolidated_dir = Path('data/pokemon_consolidated')
    
    if not pokemon_consolidated_dir.exists():
        print(f"Error: {pokemon_consolidated_dir} directory not found!")
        return
    
    print(f"Processing {len(creatures)} Pokémon...")
    
    for creature in creatures:
        db_symbol = creature.get('dbSymbol')
        form = creature.get('form', 0)
        
        # Load the individual Pokémon file
        pokemon_file = pokemon_consolidated_dir / f"{db_symbol}.json"
        
        if not pokemon_file.exists():
            print(f"Warning: {pokemon_file} not found, skipping...")
            continue
        
        try:
            pokemon_data = load_json(pokemon_file)
            forms = pokemon_data.get('forms', [])
            
            # Find the matching form
            matching_form = None
            for f in forms:
                if f.get('form') == form:
                    matching_form = f
                    break
            
            if not matching_form:
                print(f"Warning: Form {form} not found for {db_symbol}, skipping...")
                continue
            
            # Get types
            type1 = matching_form.get('type1')
            type2 = matching_form.get('type2')
            
            # Add Pokémon to type1
            if type1:
                if type1 not in types_data:
                    types_data[type1] = {
                        'count': 0,
                        'pokemon': []
                    }
                if db_symbol not in types_data[type1]['pokemon']:
                    types_data[type1]['pokemon'].append(db_symbol)
                    types_data[type1]['count'] += 1
            
            # Add Pokémon to type2 if it exists, is different from type1, and is not __undef__
            if type2 and type2 != type1 and type2 != '__undef__':
                if type2 not in types_data:
                    types_data[type2] = {
                        'count': 0,
                        'pokemon': []
                    }
                if db_symbol not in types_data[type2]['pokemon']:
                    types_data[type2]['pokemon'].append(db_symbol)
                    types_data[type2]['count'] += 1
            
            total_pokemon += 1
            
        except Exception as e:
            print(f"Error processing {db_symbol}: {e}")
            continue
    
    # Sort types alphabetically
    types_data = dict(sorted(types_data.items()))
    
    # Create final output
    output = {
        'totalPokemon': total_pokemon,
        'types': types_data
    }
    
    # Save to file
    output_path = Path('data/types_data.json')
    save_json(output, output_path)
    
    print(f"\n✓ Successfully processed {total_pokemon} Pokémon")
    print(f"✓ Found {len(types_data)} types")
    print(f"✓ Data saved to {output_path}")
    
    # Print summary
    print("\nType Summary:")
    for type_name, type_info in types_data.items():
        print(f"  {type_name.capitalize()}: {type_info['count']} Pokémon")

if __name__ == "__main__":
    process_pokemon_types()