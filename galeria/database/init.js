db = db.getSiblingDB('galeria_db');

db.obras.insertMany([
  {
    titulo: "La Joconde (Mona Lisa)",
    artista: "Leonardo da Vinci",
    año: 1503,
    tipo: "pintura",
    tecnica: "Óleo sobre tabla de álamo",
    ubicacion: "Museo del Louvre, París",
    descripcion: "Retrato de Lisa Gherardini, esposa de Francesco del Giocondo. Es la obra más famosa y visitada del mundo, célebre por la enigmática sonrisa de su protagonista.",
    imagen_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/800px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
    categorias: ["Renacimiento", "Retrato", "Óleo"]
  },
  {
    titulo: "La noche estrellada",
    artista: "Vincent van Gogh",
    año: 1889,
    tipo: "pintura",
    tecnica: "Óleo sobre lienzo",
    ubicacion: "MoMA, Nueva York",
    descripcion: "Pintada durante su internamiento en el asilo Saint-Paul-de-Mausole. Representa el cielo nocturno sobre el pueblo de Saint-Rémy-de-Provence, con un ciprés en primer plano.",
    imagen_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
    categorias: ["Postimpresionismo", "Paisaje", "Óleo"]
  },
  {
    titulo: "La persistencia de la memoria",
    artista: "Salvador Dalí",
    año: 1931,
    tipo: "pintura",
    tecnica: "Óleo sobre lienzo",
    ubicacion: "MoMA, Nueva York",
    descripcion: "Obra icónica del surrealismo que muestra relojes derritiéndose en un paisaje onírico de Port Lligat, explorando la relatividad del tiempo y el inconsciente.",
    imagen_url: "https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg",
    categorias: ["Surrealismo", "Óleo"]
  },
  {
    titulo: "La Venus de Milo",
    artista: "Alexandros de Antioquía",
    año: -130,
    tipo: "escultura",
    tecnica: "Mármol de Paros",
    ubicacion: "Museo del Louvre, París",
    descripcion: "Escultura helenística que representa a Afrodita, diosa griega del amor. Descubierta en 1820 en la isla de Melos, es célebre por sus brazos faltantes y su serena belleza.",
    imagen_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Venus_de_Milo.jpg/800px-Venus_de_Milo.jpg",
    categorias: ["Antigüedad", "Escultura", "Mármol"]
  },
  {
    titulo: "El pensador",
    artista: "Auguste Rodin",
    año: 1904,
    tipo: "escultura",
    tecnica: "Bronce",
    ubicacion: "Museo Rodin, París",
    descripcion: "Figura masculina en actitud de profunda meditación. Originalmente concebida como parte de Las Puertas del Infierno y pensada para representar a Dante contemplando su poema.",
    imagen_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Burghers_of_Calais_3.jpg/800px-Burghers_of_Calais_3.jpg",
    categorias: ["Modernismo", "Escultura", "Bronce"]
  },
  {
    titulo: "Las Meninas",
    artista: "Diego Velázquez",
    año: 1656,
    tipo: "pintura",
    tecnica: "Óleo sobre lienzo",
    ubicacion: "Museo del Prado, Madrid",
    descripcion: "Una de las obras más importantes de la pintura occidental. Representa a la infanta Margarita Teresa rodeada de su séquito, con el propio Velázquez pintando en el lienzo.",
    imagen_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Las_Meninas_01.jpg/800px-Las_Meninas_01.jpg",
    categorias: ["Barroco", "Retrato", "Óleo"]
  },
  {
    titulo: "La Creación de Adán",
    artista: "Miguel Ángel",
    año: 1512,
    tipo: "pintura",
    tecnica: "Fresco",
    ubicacion: "Capilla Sixtina, Ciudad del Vaticano",
    descripcion: "Fresco que ocupa parte del techo de la Capilla Sixtina. Representa el momento bíblico en que Dios insufla vida a Adán. El espacio entre los dedos es una de las imágenes más reconocibles del arte mundial.",
    imagen_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg/1280px-Michelangelo_-_Creation_of_Adam_%28cropped%29.jpg",
    categorias: ["Renacimiento", "Fresco", "Religioso"]
  },
  {
    titulo: "El grito",
    artista: "Edvard Munch",
    año: 1893,
    tipo: "pintura",
    tecnica: "Óleo, temple y pastel sobre cartón",
    ubicacion: "Galería Nacional de Noruega, Oslo",
    descripcion: "Representación de una figura andrógina con el rostro distorsionado por la angustia, frente a un cielo de colores vibrantes. Icono del expresionismo y la ansiedad moderna.",
    imagen_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg/800px-Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
    categorias: ["Expresionismo", "Óleo"]
  }
]);

print("✅ Galería inicializada con " + db.obras.countDocuments() + " obras de arte");
