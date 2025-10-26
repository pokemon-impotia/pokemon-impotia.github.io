document.addEventListener('DOMContentLoaded', () => {
    const typesGrid = document.getElementById('typesGrid');
    const pokemonSection = document.getElementById('pokemonSection');
    const pokemonGrid = document.getElementById('pokemonGrid');
    const selectedTypeTitle = document.getElementById('selectedTypeTitle');
    const backButton = document.getElementById('backButton');
    const totalCount = document.getElementById('totalCount');

    let typesData = null;
    let currentLanguage = 'fr';

    // Type translations
    const typeTranslations = {
        normal: { en: 'Normal', fr: 'Normal', it: 'Normale', de: 'Normal', es: 'Normal' },
        fire: { en: 'Fire', fr: 'Feu', it: 'Fuoco', de: 'Feuer', es: 'Fuego' },
        water: { en: 'Water', fr: 'Eau', it: 'Acqua', de: 'Wasser', es: 'Agua' },
        electric: { en: 'Electric', fr: 'Électrique', it: 'Elettro', de: 'Elektro', es: 'Eléctrico' },
        grass: { en: 'Grass', fr: 'Plante', it: 'Erba', de: 'Pflanze', es: 'Planta' },
        ice: { en: 'Ice', fr: 'Glace', it: 'Ghiaccio', de: 'Eis', es: 'Hielo' },
        fighting: { en: 'Fighting', fr: 'Combat', it: 'Lotta', de: 'Kampf', es: 'Lucha' },
        poison: { en: 'Poison', fr: 'Poison', it: 'Veleno', de: 'Gift', es: 'Veneno' },
        ground: { en: 'Ground', fr: 'Sol', it: 'Terra', de: 'Boden', es: 'Tierra' },
        flying: { en: 'Flying', fr: 'Vol', it: 'Volante', de: 'Flug', es: 'Volador' },
        psychic: { en: 'Psychic', fr: 'Psy', it: 'Psico', de: 'Psycho', es: 'Psíquico' },
        bug: { en: 'Bug', fr: 'Insecte', it: 'Coleottero', de: 'Käfer', es: 'Bicho' },
        rock: { en: 'Rock', fr: 'Roche', it: 'Roccia', de: 'Gestein', es: 'Roca' },
        ghost: { en: 'Ghost', fr: 'Spectre', it: 'Spettro', de: 'Geist', es: 'Fantasma' },
        dragon: { en: 'Dragon', fr: 'Dragon', it: 'Drago', de: 'Drache', es: 'Dragón' },
        dark: { en: 'Dark', fr: 'Ténèbres', it: 'Buio', de: 'Unlicht', es: 'Siniestro' },
        steel: { en: 'Steel', fr: 'Acier', it: 'Acciaio', de: 'Stahl', es: 'Acero' },
        fairy: { en: 'Fairy', fr: 'Fée', it: 'Folletto', de: 'Fee', es: 'Hada' }
    };

    // Type colors (official Pokémon colors)
    const typeColors = {
        normal: '#A8A878',
        fire: '#F08030',
        water: '#6890F0',
        electric: '#F8D030',
        grass: '#78C850',
        ice: '#98D8D8',
        fighting: '#C03028',
        poison: '#A040A0',
        ground: '#E0C068',
        flying: '#A890F0',
        psychic: '#F85888',
        bug: '#A8B820',
        rock: '#B8A038',
        ghost: '#705898',
        dragon: '#7038F8',
        dark: '#705848',
        steel: '#B8B8D0',
        fairy: '#EE99AC'
    };

    // Get current language from LanguageManager
    function getCurrentLanguage() {
        if (window.languageManager) {
            currentLanguage = window.languageManager.getCurrentLanguage();
        }
        return currentLanguage;
    }

    // Remove accents for image paths
    function removeAccents(str) {
        return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    // Get translated type name
    function getTypeName(type) {
        const lang = getCurrentLanguage();
        return typeTranslations[type]?.[lang] || type.charAt(0).toUpperCase() + type.slice(1);
    }

    // Load types data
    fetch('data/types_data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            typesData = data;
            totalCount.textContent = data.totalPokemon;
            displayTypes(data.types);
        })
        .catch(error => {
            console.error('Error loading types data:', error);
            typesGrid.innerHTML = '<p>Failed to load types data. Please try again later.</p>';
        });

    // Display type buttons
    function displayTypes(types) {
        typesGrid.innerHTML = '';

        Object.entries(types).forEach(([typeName, typeInfo]) => {
            const typeButton = document.createElement('div');
            typeButton.classList.add('type-button');
            typeButton.style.borderColor = typeColors[typeName] || '#999';

            // Type icon
            const lang = getCurrentLanguage();
            const typeFrench = removeAccents(typeTranslations[typeName]?.fr || typeName);
            const typeIcon = document.createElement('img');
            typeIcon.src = `resources/icons/types/${typeFrench.toLowerCase()}.png`;
            typeIcon.alt = typeName;
            typeIcon.classList.add('type-icon');

            // Line break
            const lineBreak = document.createElement('br');

            // Type count
            const typeCount = document.createElement('span');
            typeCount.classList.add('type-count');
            typeCount.textContent = `${typeInfo.count} Pokémon`;

            typeButton.appendChild(typeIcon);
            typeButton.appendChild(typeCount);

            // Click handler
            typeButton.addEventListener('click', () => {
                displayPokemonOfType(typeName, typeInfo.pokemon);
            });

            typesGrid.appendChild(typeButton);
        });
    }

    // Display Pokémon of selected type
    function displayPokemonOfType(typeName, pokemonList) {
        // Update title
        selectedTypeTitle.textContent = `${getTypeName(typeName)} (${pokemonList.length})`;
        
        // Hide types grid, show pokemon section
        typesGrid.style.display = 'none';
        document.getElementById('statsContainer').style.display = 'none';
        pokemonSection.classList.remove('hidden');

        // Clear previous pokemon
        pokemonGrid.innerHTML = '';

        // Display each pokemon
        pokemonList.forEach(dbSymbol => {
            const pokemonCard = document.createElement('div');
            pokemonCard.classList.add('pokemon-card');

            const spritePath = `data/pokefront/${dbSymbol}.png`;

            const pokemonSprite = document.createElement('img');
            pokemonSprite.src = spritePath;
            pokemonSprite.alt = dbSymbol;
            pokemonSprite.classList.add('pokemon-sprite');

            const pokemonName = document.createElement('p');
            pokemonName.textContent = dbSymbol.charAt(0).toUpperCase() + dbSymbol.slice(1);
            pokemonName.classList.add('pokemon-name');

            pokemonCard.appendChild(pokemonSprite);
            pokemonCard.appendChild(pokemonName);

            // Make the card clickable
            pokemonCard.addEventListener('click', () => {
                const urlParams = new URLSearchParams(window.location.search);
                const lang = urlParams.get('lang') || 'fr';
                window.location.href = `pokemon_search.html?pokemon=${dbSymbol}&lang=${lang}`;
            });

            pokemonGrid.appendChild(pokemonCard);
        });
    }

    // Back button handler
    backButton.addEventListener('click', () => {
        pokemonSection.classList.add('hidden');
        typesGrid.style.display = 'grid';
        document.getElementById('statsContainer').style.display = 'block';
        pokemonGrid.innerHTML = '';
    });
});