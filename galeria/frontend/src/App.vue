<!--
  App.vue — Galería de Arte
  ──────────────────────────
  Estrategia de imágenes:
    Cuando el usuario sube una imagen, el frontend genera DOS versiones
    usando la API Canvas del navegador:

      imagen_thumbnail → ancho máximo 500px, calidad 0.75
                         Se usa en el GRID (tarjetas). Liviana.

      imagen_data      → ancho máximo 1400px, calidad 0.90
                         Se usa en el MODAL (detalle completo). Alta calidad.

    Ambas se guardan en el documento de MongoDB.
    El endpoint GET /api/obras devuelve thumbnail (no imagen_data)
    para mantener el listado liviano.
    El endpoint GET /api/obras/:id devuelve todo, incluyendo imagen_data.

  Función de resolución de imagen:
    imagenSrcGrid(obra)  → imagen_thumbnail → imagen_url → placeholder
    imagenSrcModal(obra) → imagen_data      → imagen_url → placeholder
-->
<template>
  <div class="galeria-app">

    <!-- ═══════════════════════════════════════════════
         CABECERA
         ═══════════════════════════════════════════════ -->
    <header class="site-header">
      <div class="header-inner">
        <div class="logo">
          <span class="logo-ornament">✦</span>
          <span class="logo-text">Galería de Arte</span>
          <span class="logo-ornament">✦</span>
        </div>
        <nav class="header-nav">
          <button @click="vista = 'galeria'" :class="{ active: vista === 'galeria' }">Colección</button>
          <button @click="vista = 'submit'"  :class="{ active: vista === 'submit'  }">+ Agregar Obra</button>
        </nav>
      </div>
    </header>

    <!-- ═══════════════════════════════════════════════
         VISTA: GALERÍA
         ═══════════════════════════════════════════════ -->
    <main v-if="vista === 'galeria'" class="galeria-main">

      <section class="hero">
        <p class="hero-subtitle">Una ventana al arte universal</p>
        <h1 class="hero-title">Obras Maestras<br/><em>de la Historia</em></h1>
      </section>

      <!-- Filtros: tipo y categoría -->
      <section class="filtros-section">
        <div class="filtros-header">
          <span class="filtros-label">Filtrar por</span>
          <div class="filtros-tipo">
            <button
              v-for="t in tipos" :key="t.valor"
              @click="filtroTipo = filtroTipo === t.valor ? '' : t.valor"
              :class="['tipo-btn', { active: filtroTipo === t.valor }]"
            >{{ t.label }}</button>
          </div>
        </div>
        <div class="filtros-categorias">
          <button @click="filtroCategoria = ''" :class="['cat-chip', { active: filtroCategoria === '' }]">Todas</button>
          <button
            v-for="cat in categorias" :key="cat"
            @click="filtroCategoria = filtroCategoria === cat ? '' : cat"
            :class="['cat-chip', { active: filtroCategoria === cat }]"
          >{{ cat }}</button>
        </div>
      </section>

      <!-- Contador de resultados -->
      <div class="resultados-info">
        <span v-if="obrasFiltradas.length > 0">
          Mostrando <strong>{{ obrasFiltradas.length }}</strong>
          obra{{ obrasFiltradas.length !== 1 ? 's' : '' }}
          <span v-if="filtroCategoria"> en <em>{{ filtroCategoria }}</em></span>
          <span v-if="filtroTipo"> · {{ filtroTipo === 'pintura' ? 'Pinturas' : 'Esculturas' }}</span>
        </span>
        <span v-else class="sin-resultados">No hay obras con esos filtros.</span>
      </div>

      <div v-if="error" class="error-banner">{{ error }}</div>

      <!-- Skeleton loader mientras carga -->
      <div v-if="cargando" class="obras-grid">
        <div v-for="n in 6" :key="n" class="skeleton-card"></div>
      </div>

      <!-- Grid de obras -->
      <section v-else class="obras-grid">
        <article
          v-for="obra in obrasFiltradas" :key="obra._id"
          class="obra-card"
          @click="abrirDetalle(obra._id)"
        >
          <div class="obra-img-wrap">
            <!--
              imagenSrcGrid usa imagen_thumbnail (versión reducida guardada en MongoDB)
              o imagen_url como fallback para las obras del seed inicial.
              @error muestra placeholder si la URL externa no carga.
            -->
            <img
              :src="imagenSrcGrid(obra)"
              :alt="obra.titulo"
              class="obra-img"
              loading="lazy"
              @error="e => e.target.src = imagenPlaceholder()"
            />
            <div class="obra-tipo-badge">{{ obra.tipo }}</div>
          </div>
          <div class="obra-info">
            <div class="obra-meta">
              {{ obra.artista }} · {{ obra.año < 0 ? Math.abs(obra.año) + ' a.C.' : obra.año }}
            </div>
            <h3 class="obra-titulo">{{ obra.titulo }}</h3>
            <p class="obra-desc">{{ obra.descripcion }}</p>
            <div class="obra-cats">
              <span v-for="cat in obra.categorias" :key="cat" class="obra-cat">{{ cat }}</span>
            </div>
          </div>
        </article>
      </section>
    </main>


    <!-- ═══════════════════════════════════════════════
         MODAL: Detalle / Edición
         ═══════════════════════════════════════════════ -->
    <transition name="modal-fade">
      <div v-if="modalAbierto" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal-content">
          <button class="modal-close" @click="cerrarModal">✕</button>

          <div v-if="cargandoDetalle" class="modal-loading">Cargando obra…</div>

          <div v-else-if="obraSeleccionada" class="modal-body">

            <!-- Columna imagen -->
            <div class="modal-img-col">
              <!--
                En el modal usamos imagenSrcModal que prioriza imagen_data
                (versión completa cargada al abrir el detalle).
              -->
              <img
                :src="imagenSrcModal(obraSeleccionada)"
                :alt="obraSeleccionada.titulo"
                class="modal-img"
                @error="e => e.target.src = imagenPlaceholder()"
              />
            </div>

            <!-- Columna info / edición -->
            <div class="modal-info-col">

              <!-- ── MODO VISTA ──────────────────────────── -->
              <template v-if="!modoEdicion">
                <span class="modal-tipo">{{ obraSeleccionada.tipo }}</span>
                <h2 class="modal-titulo">{{ obraSeleccionada.titulo }}</h2>
                <p class="modal-artista">{{ obraSeleccionada.artista }}</p>
                <table class="modal-table">
                  <tr v-if="obraSeleccionada.año">
                    <td class="tl">Año</td>
                    <td>{{ obraSeleccionada.año < 0 ? Math.abs(obraSeleccionada.año) + ' a.C.' : obraSeleccionada.año }}</td>
                  </tr>
                  <tr v-if="obraSeleccionada.tecnica">
                    <td class="tl">Técnica</td>
                    <td>{{ obraSeleccionada.tecnica }}</td>
                  </tr>
                  <tr v-if="obraSeleccionada.ubicacion">
                    <td class="tl">Ubicación</td>
                    <td>{{ obraSeleccionada.ubicacion }}</td>
                  </tr>
                </table>
                <p class="modal-desc">{{ obraSeleccionada.descripcion }}</p>
                <div class="modal-cats">
                  <span v-for="cat in obraSeleccionada.categorias" :key="cat" class="obra-cat">{{ cat }}</span>
                </div>
                <div class="modal-actions">
                  <button class="btn-editar" @click="activarEdicion">✎ Editar obra</button>
                  <button class="btn-eliminar" @click="eliminarObra(obraSeleccionada._id)">✕ Eliminar</button>
                </div>
              </template>

              <!-- ── MODO EDICIÓN ────────────────────────── -->
              <template v-else>
                <h3 class="edit-title">Editando obra</h3>
                <div class="edit-scroll">

                  <div class="form-group">
                    <label>Título *</label>
                    <input v-model="formEdit.titulo" />
                  </div>
                  <div class="form-group">
                    <label>Artista *</label>
                    <input v-model="formEdit.artista" />
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Año *</label>
                      <input v-model="formEdit.año" type="number" />
                    </div>
                    <div class="form-group">
                      <label>Tipo *</label>
                      <select v-model="formEdit.tipo">
                        <option value="pintura">Pintura</option>
                        <option value="escultura">Escultura</option>
                      </select>
                    </div>
                  </div>
                  <div class="form-group">
                    <label>Técnica</label>
                    <input v-model="formEdit.tecnica" />
                  </div>
                  <div class="form-group">
                    <label>Ubicación</label>
                    <input v-model="formEdit.ubicacion" />
                  </div>
                  <div class="form-group">
                    <label>Descripción</label>
                    <textarea v-model="formEdit.descripcion" rows="3"></textarea>
                  </div>

                  <!-- Selector de imagen en edición -->
                  <div class="form-group">
                    <label>Imagen (reemplazar)</label>
                    <input
                      type="file" accept="image/*"
                      ref="inputImagenEdit"
                      @change="onImagenEditCambiada"
                      class="file-input"
                    />
                    <!-- Preview: nueva imagen seleccionada o la actual -->
                    <div class="img-preview-wrap">
                      <img
                        :src="formEdit.previewEdit || imagenSrcModal(obraSeleccionada)"
                        class="img-preview"
                        @error="e => e.target.src = imagenPlaceholder()"
                      />
                      <span v-if="formEdit.previewEdit"  class="img-nueva-badge">✓ Nueva imagen lista</span>
                      <span v-else                        class="img-actual-badge">Imagen actual</span>
                    </div>
                  </div>

                  <!-- Categorías en edición -->
                  <div class="form-group">
                    <label>Categorías</label>
                    <div class="cats-selector">
                      <button
                        v-for="cat in categoriasDisponibles" :key="cat"
                        type="button"
                        @click="toggleCategoriaEdit(cat)"
                        :class="['cat-chip', { active: formEdit.categorias.includes(cat) }]"
                      >{{ cat }}</button>
                    </div>
                    <div class="cat-custom">
                      <input v-model="nuevaCategoriaEdit" placeholder="Nueva categoría..." @keyup.enter="agregarCategoriaEdit" />
                      <button type="button" @click="agregarCategoriaEdit">+</button>
                    </div>
                  </div>

                </div><!-- /edit-scroll -->

                <div v-if="editError"  class="error-banner mt-1">{{ editError }}</div>
                <div v-if="editExito"  class="exito-banner mt-1">✓ Cambios guardados</div>

                <div class="modal-actions">
                  <button class="btn-secundario" @click="cancelarEdicion">Cancelar</button>
                  <button class="btn-primary" @click="guardarEdicion" :disabled="guardando">
                    {{ guardando ? 'Guardando...' : '✓ Guardar cambios' }}
                  </button>
                </div>
              </template>

            </div><!-- /modal-info-col -->
          </div><!-- /modal-body -->
        </div><!-- /modal-content -->
      </div><!-- /modal-overlay -->
    </transition>


    <!-- ═══════════════════════════════════════════════
         VISTA: NUEVA OBRA
         ═══════════════════════════════════════════════ -->
    <main v-if="vista === 'submit'" class="submit-main">
      <div class="submit-container">
        <div class="submit-header">
          <span class="logo-ornament">✦</span>
          <h2>Registrar Nueva Obra</h2>
          <span class="logo-ornament">✦</span>
        </div>

        <div class="form-grid">
          <!-- Columna izquierda: campos de texto -->
          <div class="form-col">
            <div class="form-group">
              <label>Título *</label>
              <input v-model="form.titulo" placeholder="Nombre de la obra" />
            </div>
            <div class="form-group">
              <label>Artista *</label>
              <input v-model="form.artista" placeholder="Nombre del artista" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Año *</label>
                <input v-model="form.año" type="number" placeholder="ej: 1889" />
              </div>
              <div class="form-group">
                <label>Tipo *</label>
                <select v-model="form.tipo">
                  <option value="pintura">Pintura</option>
                  <option value="escultura">Escultura</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label>Técnica</label>
              <input v-model="form.tecnica" placeholder="ej: Óleo sobre lienzo" />
            </div>
            <div class="form-group">
              <label>Ubicación</label>
              <input v-model="form.ubicacion" placeholder="Museo o colección" />
            </div>
            <div class="form-group">
              <label>Descripción</label>
              <textarea v-model="form.descripcion" rows="5" placeholder="Historia y contexto..."></textarea>
            </div>
          </div>

          <!-- Columna derecha: imagen y categorías -->
          <div class="form-col">
            <div class="form-group">
              <label>Imagen de la obra</label>
              <!--
                Al seleccionar un archivo, onImagenCambiada() lo procesa:
                1. Llama a crearThumbnail(file, 500, 0.75) → imagen_thumbnail (para el grid)
                2. Llama a crearThumbnail(file, 1400, 0.90) → imagen_data (para el modal)
                Ambas se almacenan en MongoDB al enviar el formulario.
              -->
              <input type="file" accept="image/*" ref="inputImagen" @change="onImagenCambiada" class="file-input" />
              <!-- Indicador de procesamiento de imagen -->
              <div v-if="procesandoImagen" class="procesando-img">
                ⏳ Procesando imagen...
              </div>
              <!-- Preview de la imagen seleccionada (usa el thumbnail generado) -->
              <div v-if="form.imagen_thumbnail" class="img-preview-wrap">
                <img :src="form.imagen_thumbnail" class="img-preview" />
                <span class="img-nueva-badge">✓ Imagen lista (thumbnail + completa)</span>
              </div>
            </div>

            <div class="form-group">
              <label>Categorías</label>
              <div class="cats-selector">
                <button
                  v-for="cat in categoriasDisponibles" :key="cat"
                  type="button"
                  @click="toggleCategoria(cat)"
                  :class="['cat-chip', { active: form.categorias.includes(cat) }]"
                >{{ cat }}</button>
              </div>
              <div class="cat-custom">
                <input v-model="nuevaCategoria" placeholder="Nueva categoría..." @keyup.enter="agregarCategoria" />
                <button type="button" @click="agregarCategoria">+</button>
              </div>
            </div>
          </div>
        </div><!-- /form-grid -->

        <div v-if="submitError" class="error-banner">{{ submitError }}</div>
        <div v-if="submitExito" class="exito-banner">✓ Obra registrada correctamente</div>

        <div class="form-actions">
          <button @click="vista = 'galeria'" class="btn-secundario">← Volver</button>
          <button @click="enviarObra" :disabled="enviando || procesandoImagen" class="btn-primary">
            {{ enviando ? 'Guardando...' : 'Registrar Obra' }}
          </button>
        </div>
      </div>
    </main>

    <footer class="site-footer">
      <p>Galería de Arte · Microservicios Docker · Vue + Flask + MongoDB</p>
    </footer>
  </div>
</template>


<script>
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Categorías predefinidas para los selectores del formulario
const CATS_DEFAULT = [
  'Renacimiento', 'Barroco', 'Impresionismo', 'Postimpresionismo',
  'Expresionismo', 'Surrealismo', 'Abstracto', 'Modernismo',
  'Antigüedad', 'Retrato', 'Paisaje', 'Religioso',
  'Óleo', 'Fresco', 'Mármol', 'Bronce'
]

// Objeto de formulario vacío para nueva obra
const formVacio = () => ({
  titulo: '', artista: '', año: '', tipo: 'pintura',
  tecnica: '', ubicacion: '', descripcion: '',
  imagen_thumbnail: '',   // Base64 reducida → grid
  imagen_data:      '',   // Base64 completa → modal
  categorias: [],
})

export default {
  name: 'App',

  data() {
    return {
      vista: 'galeria',
      obras: [],
      categorias: [],
      categoriasDisponibles: [...CATS_DEFAULT],
      filtroCategoria: '',
      filtroTipo: '',
      tipos: [
        { valor: 'pintura',   label: '🖼 Pintura'   },
        { valor: 'escultura', label: '🗿 Escultura' },
      ],
      cargando: false,
      error: null,

      // Estado del modal
      modalAbierto: false,
      obraSeleccionada: null,
      cargandoDetalle: false,

      // Estado de edición
      modoEdicion: false,
      formEdit: {},
      nuevaCategoriaEdit: '',
      guardando: false,
      editError: null,
      editExito: false,

      // Estado del formulario de nueva obra
      form: formVacio(),
      nuevaCategoria: '',
      enviando: false,
      submitError: null,
      submitExito: false,
      procesandoImagen: false,   // true mientras Canvas procesa la imagen
    }
  },

  computed: {
    // Filtra obras según los filtros activos (filtrado local, sin petición al backend)
    obrasFiltradas() {
      return this.obras.filter(o => {
        const matchCat  = !this.filtroCategoria || (o.categorias || []).includes(this.filtroCategoria)
        const matchTipo = !this.filtroTipo || o.tipo === this.filtroTipo
        return matchCat && matchTipo
      })
    }
  },

  mounted() {
    this.cargarObras()
    this.cargarCategorias()
  },

  methods: {

    // ── Resolución de imagen ────────────────────────────────────────────────

    /**
     * imagenSrcGrid: fuente de imagen para las tarjetas del grid.
     * Prioridad: imagen_thumbnail (Base64 reducida) → imagen_url (URL externa seed)
     * El backend incluye imagen_thumbnail en el listado (campo liviano).
     */
    imagenSrcGrid(obra) {
      if (!obra) return this.imagenPlaceholder()
      if (obra.imagen_thumbnail) return obra.imagen_thumbnail   // Base64 guardada en Mongo
      if (obra.imagen_url)       return obra.imagen_url          // URL externa de fallback
      return this.imagenPlaceholder()
    },

    /**
     * imagenSrcModal: fuente de imagen para el modal de detalle.
     * Prioridad: imagen_data (Base64 completa) → imagen_url → placeholder
     * imagen_data solo viene del endpoint GET /api/obras/:id (detalle individual).
     */
    imagenSrcModal(obra) {
      if (!obra) return this.imagenPlaceholder()
      if (obra.imagen_data)      return obra.imagen_data         // Base64 completa
      if (obra.imagen_url)       return obra.imagen_url
      return this.imagenPlaceholder()
    },

    imagenPlaceholder() {
      return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300' viewBox='0 0 400 300'%3E%3Crect width='400' height='300' fill='%231a1a16'/%3E%3Ctext x='50%25' y='45%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='13' fill='%23666'%3ESin imagen%3C/text%3E%3Ctext x='50%25' y='58%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='22' fill='%23444'%3E%F0%9F%96%BC%3C/text%3E%3C/svg%3E"
    },

    // ── Generación de imagen redimensionada con Canvas ─────────────────────

    /**
     * crearThumbnail: redimensiona una imagen usando la API Canvas del navegador
     * y la devuelve como cadena Base64 (Data URL).
     *
     * @param {File}   archivo    - Archivo de imagen seleccionado por el usuario
     * @param {number} maxAncho   - Ancho máximo en píxeles (alto se ajusta proporcionalmente)
     * @param {number} calidad    - Calidad JPEG de 0 a 1 (0.75 = thumbnail, 0.90 = completa)
     * @returns {Promise<string>} - Promesa que resuelve con la cadena Base64
     *
     * Flujo:
     *   1. FileReader lee el archivo como Data URL
     *   2. Se crea un <img> temporal en memoria para obtener las dimensiones reales
     *   3. Se crea un <canvas> con las dimensiones proporcionales al maxAncho
     *   4. Se dibuja la imagen en el canvas con drawImage()
     *   5. canvas.toDataURL() convierte el canvas a cadena Base64
     */
    crearThumbnail(archivo, maxAncho, calidad) {
      return new Promise((resolve, reject) => {

        // Paso 1: leer el archivo como Data URL
        const reader = new FileReader()
        reader.readAsDataURL(archivo)    // Inicia la lectura asíncrona del archivo

        reader.onload = (e) => {
          // Paso 2: crear un elemento <img> temporal para obtener las dimensiones reales
          const img = new Image()
          img.src = e.target.result    // Asigna el Data URL al src del img temporal

          img.onload = () => {
            // Calcular las dimensiones proporcionales respetando el maxAncho
            let ancho = img.width
            let alto  = img.height

            if (ancho > maxAncho) {
              // Solo redimensionar si la imagen es más ancha que el máximo
              alto  = Math.round((alto * maxAncho) / ancho)   // Mantener proporción
              ancho = maxAncho
            }
            // Si la imagen ya es más pequeña que maxAncho, se usa tal cual

            // Paso 3: crear un <canvas> con las dimensiones calculadas
            const canvas = document.createElement('canvas')
            canvas.width  = ancho
            canvas.height = alto

            // Paso 4: obtener el contexto 2D y dibujar la imagen redimensionada
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, ancho, alto)   // Dibuja img en el canvas con el nuevo tamaño

            // Paso 5: exportar el canvas como cadena Base64 JPEG
            // 'image/jpeg' produce archivos más pequeños que 'image/png'
            const base64 = canvas.toDataURL('image/jpeg', calidad)
            resolve(base64)   // Devuelve la cadena Base64 a quien llamó crearThumbnail()
          }

          img.onerror = () => reject(new Error('No se pudo cargar la imagen'))
        }

        reader.onerror = () => reject(new Error('Error al leer el archivo'))
      })
    },

    // ── Manejadores de input de imagen ─────────────────────────────────────

    /**
     * onImagenCambiada: se ejecuta cuando el usuario elige un archivo en el form de nueva obra.
     * Genera las dos versiones en paralelo con Promise.all para mayor eficiencia.
     */
    async onImagenCambiada(event) {
      const archivo = event.target.files[0]
      if (!archivo) return

      this.procesandoImagen = true    // Muestra el indicador de procesamiento
      try {
        // Genera thumbnail y versión completa en paralelo (simultáneamente)
        const [thumbnail, completa] = await Promise.all([
          this.crearThumbnail(archivo, 500,  0.75),   // 500px ancho, calidad 75% → grid
          this.crearThumbnail(archivo, 1400, 0.90),   // 1400px ancho, calidad 90% → modal
        ])
        this.form.imagen_thumbnail = thumbnail   // Se envía al backend y se muestra en el grid
        this.form.imagen_data      = completa    // Se envía al backend y se usa en el modal
      } catch {
        this.submitError = 'Error al procesar la imagen. Intenta con otro archivo.'
      } finally {
        this.procesandoImagen = false
      }
    },

    /**
     * onImagenEditCambiada: igual que onImagenCambiada pero para el formulario de edición.
     * Las dos versiones se guardan en formEdit y se envían al backend en guardarEdicion().
     */
    async onImagenEditCambiada(event) {
      const archivo = event.target.files[0]
      if (!archivo) return

      this.procesandoImagen = true
      try {
        const [thumbnail, completa] = await Promise.all([
          this.crearThumbnail(archivo, 500,  0.75),
          this.crearThumbnail(archivo, 1400, 0.90),
        ])
        // previewEdit: cadena Base64 para mostrar el preview en el modal
        // Se usa el thumbnail (más liviano) para el preview en tiempo real
        this.formEdit.previewEdit         = thumbnail
        this.formEdit.imagen_thumbnail_nueva = thumbnail
        this.formEdit.imagen_data_nueva      = completa
      } catch {
        this.editError = 'Error al procesar la imagen.'
      } finally {
        this.procesandoImagen = false
      }
    },

    // ── Carga de datos ──────────────────────────────────────────────────────

    async cargarObras() {
      this.cargando = true
      this.error = null
      try {
        const res = await axios.get(`${API}/api/obras`)
        // Cada obra en la lista incluye imagen_thumbnail pero NO imagen_data
        this.obras = res.data
      } catch {
        this.error = 'No se pudo conectar con el backend. Verifica que los contenedores estén activos.'
      } finally {
        this.cargando = false
      }
    },

    async cargarCategorias() {
      try {
        const res = await axios.get(`${API}/api/categorias`)
        this.categorias = res.data
        // Combinar categorías de la BD con las predefinidas (sin duplicados)
        this.categoriasDisponibles = [...new Set([...CATS_DEFAULT, ...res.data])]
      } catch { /* Silencioso: se usan las categorías predefinidas */ }
    },

    // ── Modal ───────────────────────────────────────────────────────────────

    /**
     * abrirDetalle: abre el modal y carga el detalle completo de la obra.
     * Se necesita una petición adicional al endpoint /:id porque el listado
     * no incluye imagen_data (se excluye para mantener el listado liviano).
     */
    async abrirDetalle(id) {
      this.modalAbierto = true
      this.cargandoDetalle = true
      this.modoEdicion = false
      this.obraSeleccionada = null
      this.editError = null
      this.editExito = false
      try {
        const res = await axios.get(`${API}/api/obras/${id}`)
        // Este endpoint SÍ incluye imagen_data → se usa en imagenSrcModal()
        this.obraSeleccionada = res.data
      } catch {
        this.cerrarModal()
      } finally {
        this.cargandoDetalle = false
      }
    },

    cerrarModal() {
      this.modalAbierto = false
      this.obraSeleccionada = null
      this.modoEdicion = false
      this.formEdit = {}
      this.editError = null
      this.editExito = false
      this.nuevaCategoriaEdit = ''
    },

    // ── Edición ─────────────────────────────────────────────────────────────

    /**
     * activarEdicion: copia los datos actuales al formulario de edición.
     * Las categorías se copian con .slice() para independizar el array.
     */
    activarEdicion() {
      this.modoEdicion = true
      this.editError = null
      this.editExito = false
      this.formEdit = {
        titulo:      this.obraSeleccionada.titulo      || '',
        artista:     this.obraSeleccionada.artista     || '',
        año:         this.obraSeleccionada.año         || '',
        tipo:        this.obraSeleccionada.tipo        || 'pintura',
        tecnica:     this.obraSeleccionada.tecnica     || '',
        ubicacion:   this.obraSeleccionada.ubicacion   || '',
        descripcion: this.obraSeleccionada.descripcion || '',
        imagen_url:  this.obraSeleccionada.imagen_url  || '',
        categorias:  (this.obraSeleccionada.categorias || []).slice(),

        // Campos temporales para las nuevas imágenes (vacíos = no hay cambio)
        previewEdit:            '',
        imagen_thumbnail_nueva: '',
        imagen_data_nueva:      '',
      }
    },

    cancelarEdicion() {
      this.modoEdicion = false
      this.editError = null
      this.editExito = false
      this.formEdit = {}
      this.nuevaCategoriaEdit = ''
    },

    async guardarEdicion() {
      this.editError = null
      this.editExito = false

      if (!this.formEdit.titulo || !this.formEdit.artista || !this.formEdit.año) {
        this.editError = 'Título, Artista y Año son obligatorios.'
        return
      }

      this.guardando = true

      const payload = {
        titulo:      this.formEdit.titulo,
        artista:     this.formEdit.artista,
        año:         Number(this.formEdit.año),
        tipo:        this.formEdit.tipo,
        tecnica:     this.formEdit.tecnica,
        ubicacion:   this.formEdit.ubicacion,
        descripcion: this.formEdit.descripcion,
        imagen_url:  this.formEdit.imagen_url,
        categorias:  this.formEdit.categorias,
      }

      // Solo enviar imágenes nuevas si el usuario seleccionó un archivo
      if (this.formEdit.imagen_thumbnail_nueva) {
        payload.imagen_thumbnail = this.formEdit.imagen_thumbnail_nueva
        payload.imagen_data      = this.formEdit.imagen_data_nueva
      }

      try {
        const res = await axios.put(`${API}/api/obras/${this.obraSeleccionada._id}`, payload)
        this.editExito = true

        // Actualizar obraSeleccionada: backend devuelve la obra sin imagen_data,
        // así que la conservamos del estado anterior o de la nueva
        this.obraSeleccionada = {
          ...res.data,
          imagen_data: this.formEdit.imagen_data_nueva || this.obraSeleccionada.imagen_data,
        }

        await this.cargarObras()
        await this.cargarCategorias()

        setTimeout(() => {
          this.modoEdicion = false
          this.editExito = false
        }, 1200)
      } catch {
        this.editError = 'Error al guardar los cambios. Intenta de nuevo.'
      } finally {
        this.guardando = false
      }
    },

    // ── Eliminar ────────────────────────────────────────────────────────────

    async eliminarObra(id) {
      if (!confirm('¿Eliminar esta obra permanentemente?')) return
      try {
        await axios.delete(`${API}/api/obras/${id}`)
        this.cerrarModal()
        await this.cargarObras()
        await this.cargarCategorias()
      } catch {
        alert('No se pudo eliminar la obra.')
      }
    },

    // ── Categorías ──────────────────────────────────────────────────────────

    toggleCategoria(cat) {
      const idx = this.form.categorias.indexOf(cat)
      if (idx === -1) this.form.categorias.push(cat)
      else            this.form.categorias.splice(idx, 1)
    },
    agregarCategoria() {
      const cat = this.nuevaCategoria.trim()
      if (!cat) return
      if (!this.categoriasDisponibles.includes(cat)) this.categoriasDisponibles.push(cat)
      if (!this.form.categorias.includes(cat))       this.form.categorias.push(cat)
      this.nuevaCategoria = ''
    },
    toggleCategoriaEdit(cat) {
      const idx = this.formEdit.categorias.indexOf(cat)
      if (idx === -1) this.formEdit.categorias.push(cat)
      else            this.formEdit.categorias.splice(idx, 1)
    },
    agregarCategoriaEdit() {
      const cat = this.nuevaCategoriaEdit.trim()
      if (!cat) return
      if (!this.categoriasDisponibles.includes(cat)) this.categoriasDisponibles.push(cat)
      if (!this.formEdit.categorias.includes(cat))   this.formEdit.categorias.push(cat)
      this.nuevaCategoriaEdit = ''
    },

    // ── Enviar nueva obra ───────────────────────────────────────────────────

    async enviarObra() {
      this.submitError = null
      this.submitExito = false

      if (!this.form.titulo || !this.form.artista || !this.form.año) {
        this.submitError = 'Completa los campos obligatorios: Título, Artista y Año.'
        return
      }

      this.enviando = true
      try {
        await axios.post(`${API}/api/obras`, {
          ...this.form,
          año: Number(this.form.año)
        })
        this.submitExito = true
        this.form = formVacio()
        await this.cargarObras()
        await this.cargarCategorias()
        setTimeout(() => { this.vista = 'galeria' }, 1500)
      } catch {
        this.submitError = 'Error al registrar la obra. Verifica la conexión.'
      } finally {
        this.enviando = false
      }
    },
  }
}
</script>


<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --negro:     #0a0a08;
  --oscuro:    #111109;
  --carbon:    #1a1a17;
  --marron:    #2a2318;
  --oro:       #c9a84c;
  --oro-claro: #e8c96a;
  --crema:     #f5f0e8;
  --gris:      #888070;
  --blanco:    #faf8f4;
  --ff-serif: 'Cormorant Garamond', Georgia, serif;
  --ff-sans:  'Montserrat', sans-serif;
}
body { background: var(--negro); color: var(--crema); font-family: var(--ff-sans); font-weight: 300; min-height: 100vh; }

/* HEADER */
.site-header { background: var(--oscuro); border-bottom: 1px solid rgba(201,168,76,0.25); position: sticky; top: 0; z-index: 100; }
.header-inner { max-width: 1300px; margin: 0 auto; padding: 0 2rem; display: flex; align-items: center; justify-content: space-between; height: 64px; }
.logo { display: flex; align-items: center; gap: 0.75rem; font-family: var(--ff-serif); font-size: 1.25rem; letter-spacing: 0.08em; color: var(--crema); }
.logo-ornament { color: var(--oro); font-size: 0.85rem; }
.header-nav { display: flex; gap: 0.5rem; }
.header-nav button { background: none; border: none; cursor: pointer; color: var(--gris); font-family: var(--ff-sans); font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase; padding: 0.4rem 1rem; border-bottom: 2px solid transparent; transition: color .2s, border-color .2s; }
.header-nav button:hover, .header-nav button.active { color: var(--oro); border-bottom-color: var(--oro); }

/* HERO */
.hero { text-align: center; padding: 5rem 2rem 3rem; background: linear-gradient(180deg, var(--oscuro) 0%, var(--negro) 100%); border-bottom: 1px solid rgba(201,168,76,0.12); }
.hero-subtitle { font-size: 0.75rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--oro); margin-bottom: 1rem; }
.hero-title { font-family: var(--ff-serif); font-size: clamp(2.5rem, 6vw, 5rem); font-weight: 300; line-height: 1.1; color: var(--blanco); }
.hero-title em { color: var(--oro); font-style: italic; }

/* FILTROS */
.filtros-section { max-width: 1300px; margin: 2.5rem auto 0; padding: 0 2rem; }
.filtros-header { display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
.filtros-label { font-size: 0.72rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--gris); }
.filtros-tipo { display: flex; gap: 0.5rem; }
.tipo-btn { background: transparent; border: 1px solid rgba(201,168,76,0.3); color: var(--gris); cursor: pointer; font-family: var(--ff-sans); font-size: 0.75rem; letter-spacing: 0.08em; padding: 0.35rem 0.9rem; border-radius: 2px; transition: all .2s; }
.tipo-btn:hover, .tipo-btn.active { background: rgba(201,168,76,0.15); border-color: var(--oro); color: var(--oro-claro); }
.filtros-categorias { display: flex; gap: 0.4rem; flex-wrap: wrap; }

/* CHIPS */
.cat-chip { background: transparent; border: 1px solid rgba(201,168,76,0.2); color: var(--gris); cursor: pointer; font-family: var(--ff-sans); font-size: 0.72rem; padding: 0.28rem 0.75rem; border-radius: 100px; transition: all .2s; }
.cat-chip:hover, .cat-chip.active { background: var(--oro); border-color: var(--oro); color: var(--negro); font-weight: 500; }

/* RESULTADOS */
.resultados-info { max-width: 1300px; margin: 1.5rem auto 0; padding: 0 2rem; font-size: 0.8rem; color: var(--gris); }
.resultados-info strong { color: var(--crema); }
.resultados-info em { color: var(--oro); font-style: normal; }
.sin-resultados { color: var(--gris); }

/* BANNERS */
.error-banner { max-width: 1300px; margin: 1rem auto; padding: 0.75rem 1.5rem; border: 1px solid #8b3a3a; background: rgba(139,58,58,0.15); color: #e87070; font-size: 0.85rem; border-radius: 4px; }
.exito-banner { max-width: 1300px; margin: 1rem auto; padding: 0.75rem 1.5rem; border: 1px solid rgba(100,180,100,0.4); background: rgba(60,120,60,0.2); color: #9de89d; font-size: 0.85rem; border-radius: 4px; }
.mt-1 { margin-top: 0.75rem; }

/* SKELETON */
.skeleton-card { height: 440px; border-radius: 4px; background: linear-gradient(90deg, var(--carbon) 25%, var(--marron) 50%, var(--carbon) 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; }
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

/* GRID */
.obras-grid { max-width: 1300px; margin: 2rem auto 4rem; padding: 0 2rem; display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }

/* TARJETA */
.obra-card { background: var(--carbon); border: 1px solid rgba(201,168,76,0.1); border-radius: 4px; overflow: hidden; cursor: pointer; transition: transform .25s, border-color .25s, box-shadow .25s; }
.obra-card:hover { transform: translateY(-4px); border-color: rgba(201,168,76,0.4); box-shadow: 0 12px 40px rgba(0,0,0,0.5); }
.obra-img-wrap { position: relative; overflow: hidden; height: 260px; background: var(--marron); }
.obra-img { width: 100%; height: 100%; object-fit: cover; object-position: top center; transition: transform .4s; }
.obra-card:hover .obra-img { transform: scale(1.04); }
.obra-tipo-badge { position: absolute; top: 0.75rem; right: 0.75rem; background: rgba(10,10,8,0.75); backdrop-filter: blur(6px); color: var(--oro); font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase; padding: 0.25rem 0.6rem; border-radius: 2px; border: 1px solid rgba(201,168,76,0.3); }
.obra-info { padding: 1.25rem 1.4rem 1.4rem; }
.obra-meta { font-size: 0.72rem; letter-spacing: 0.1em; color: var(--oro); text-transform: uppercase; margin-bottom: 0.4rem; }
.obra-titulo { font-family: var(--ff-serif); font-size: 1.35rem; font-weight: 400; color: var(--blanco); margin-bottom: 0.6rem; line-height: 1.2; }
.obra-desc { font-size: 0.8rem; color: var(--gris); line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 0.9rem; }
.obra-cats { display: flex; gap: 0.35rem; flex-wrap: wrap; }
.obra-cat { font-size: 0.65rem; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(201,168,76,0.3); color: var(--oro); padding: 0.18rem 0.55rem; border-radius: 2px; }

/* MODAL */
.modal-overlay { position: fixed; inset: 0; z-index: 200; background: rgba(0,0,0,0.85); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; padding: 1.5rem; }
.modal-content { background: var(--carbon); border: 1px solid rgba(201,168,76,0.25); border-radius: 6px; max-width: 920px; width: 100%; max-height: 90vh; overflow-y: auto; position: relative; }
.modal-loading { padding: 4rem; text-align: center; color: var(--gris); font-size: 0.85rem; letter-spacing: 0.1em; }
.modal-close { position: absolute; top: 1rem; right: 1rem; z-index: 10; background: none; border: 1px solid rgba(201,168,76,0.3); color: var(--gris); cursor: pointer; font-size: 0.85rem; width: 32px; height: 32px; border-radius: 50%; transition: all .2s; }
.modal-close:hover { background: var(--oro); color: var(--negro); }
.modal-body { display: grid; grid-template-columns: 1fr 1fr; }
@media (max-width: 640px) { .modal-body { grid-template-columns: 1fr; } }
.modal-img-col { background: var(--marron); min-height: 350px; }
.modal-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.modal-info-col { padding: 2rem 1.75rem; overflow-y: auto; max-height: 90vh; }
.modal-tipo { font-size: 0.68rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--oro); display: block; margin-bottom: 0.75rem; }
.modal-titulo { font-family: var(--ff-serif); font-size: 1.9rem; font-weight: 400; color: var(--blanco); line-height: 1.15; margin-bottom: 0.4rem; }
.modal-artista { font-size: 0.85rem; color: var(--gris); margin-bottom: 1.5rem; font-style: italic; }
.modal-table { width: 100%; border-collapse: collapse; margin-bottom: 1.25rem; }
.modal-table tr { border-bottom: 1px solid rgba(201,168,76,0.08); }
.modal-table td { padding: 0.45rem 0; font-size: 0.8rem; vertical-align: top; }
.modal-table .tl { color: var(--gris); width: 80px; font-size: 0.72rem; letter-spacing: 0.05em; }
.modal-desc { font-size: 0.82rem; color: var(--gris); line-height: 1.7; margin-bottom: 1.25rem; }
.modal-cats { display: flex; gap: 0.35rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.modal-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid rgba(201,168,76,0.1); }
.btn-editar { background: rgba(201,168,76,0.12); border: 1px solid rgba(201,168,76,0.4); color: var(--oro); cursor: pointer; font-family: var(--ff-sans); font-size: 0.75rem; letter-spacing: 0.08em; padding: 0.5rem 1.1rem; border-radius: 3px; transition: all .2s; }
.btn-editar:hover { background: rgba(201,168,76,0.25); }
.btn-eliminar { background: none; border: 1px solid rgba(200,80,80,0.4); color: #c87070; cursor: pointer; font-family: var(--ff-sans); font-size: 0.75rem; letter-spacing: 0.08em; padding: 0.5rem 1.1rem; border-radius: 3px; transition: all .2s; }
.btn-eliminar:hover { background: rgba(200,80,80,0.2); color: #e09090; }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity .25s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

/* EDICIÓN */
.edit-title { font-family: var(--ff-serif); font-size: 1.4rem; font-weight: 400; color: var(--blanco); margin-bottom: 1.25rem; }
.edit-scroll { overflow-y: auto; max-height: 55vh; padding-right: 0.25rem; display: flex; flex-direction: column; gap: 1rem; }

/* BADGES DE IMAGEN */
.img-nueva-badge, .img-actual-badge { display: block; margin-top: 0.35rem; font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; }
.img-nueva-badge  { color: #9de89d; }
.img-actual-badge { color: var(--gris); }
.procesando-img { font-size: 0.78rem; color: var(--oro); margin-top: 0.5rem; letter-spacing: 0.05em; }

/* FORMULARIO NUEVA OBRA */
.submit-main { min-height: calc(100vh - 64px); background: linear-gradient(180deg, var(--oscuro) 0%, var(--negro) 60%); padding: 4rem 2rem; }
.submit-container { max-width: 900px; margin: 0 auto; background: var(--carbon); border: 1px solid rgba(201,168,76,0.2); border-radius: 6px; padding: 3rem; }
.submit-header { text-align: center; margin-bottom: 2.5rem; display: flex; align-items: center; justify-content: center; gap: 1rem; }
.submit-header h2 { font-family: var(--ff-serif); font-size: 2rem; font-weight: 400; color: var(--blanco); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
@media (max-width: 680px) { .form-grid { grid-template-columns: 1fr; } }
.form-col { display: flex; flex-direction: column; gap: 1.2rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-group label { font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--oro); }
.form-group input, .form-group select, .form-group textarea { background: var(--marron); border: 1px solid rgba(201,168,76,0.2); color: var(--blanco); font-family: var(--ff-sans); font-size: 0.85rem; font-weight: 300; padding: 0.6rem 0.85rem; border-radius: 3px; outline: none; transition: border-color .2s; }
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: var(--oro); }
.form-group select option { background: var(--marron); }
.form-group textarea { resize: vertical; }
.file-input { padding: 0.5rem !important; cursor: pointer; }
.file-input::file-selector-button { background: rgba(201,168,76,0.15); border: 1px solid rgba(201,168,76,0.3); color: var(--oro); padding: 0.3rem 0.75rem; border-radius: 2px; cursor: pointer; font-size: 0.75rem; margin-right: 0.75rem; transition: background .2s; }
.file-input::file-selector-button:hover { background: rgba(201,168,76,0.3); }
.img-preview-wrap { margin-top: 0.5rem; }
.img-preview { width: 100%; max-height: 180px; object-fit: cover; border-radius: 3px; border: 1px solid rgba(201,168,76,0.2); display: block; }
.cats-selector { display: flex; gap: 0.35rem; flex-wrap: wrap; margin-bottom: 0.6rem; }
.cat-custom { display: flex; gap: 0.5rem; }
.cat-custom input { flex: 1; }
.cat-custom button { background: rgba(201,168,76,0.15); border: 1px solid rgba(201,168,76,0.3); color: var(--oro); cursor: pointer; font-size: 1rem; padding: 0 0.8rem; border-radius: 3px; transition: all .2s; }
.cat-custom button:hover { background: var(--oro); color: var(--negro); }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2.5rem; padding-top: 2rem; border-top: 1px solid rgba(201,168,76,0.15); }
.btn-primary { background: var(--oro); border: none; color: var(--negro); font-family: var(--ff-sans); font-size: 0.8rem; letter-spacing: 0.12em; text-transform: uppercase; padding: 0.7rem 2rem; border-radius: 3px; cursor: pointer; transition: background .2s; }
.btn-primary:hover { background: var(--oro-claro); }
.btn-primary:disabled { background: var(--gris); cursor: default; }
.btn-secundario { background: none; border: 1px solid rgba(201,168,76,0.3); color: var(--gris); cursor: pointer; font-family: var(--ff-sans); font-size: 0.8rem; letter-spacing: 0.08em; padding: 0.7rem 1.5rem; border-radius: 3px; transition: all .2s; }
.btn-secundario:hover { border-color: var(--oro); color: var(--oro); }

/* FOOTER */
.site-footer { background: var(--oscuro); border-top: 1px solid rgba(201,168,76,0.1); text-align: center; padding: 1.5rem; font-size: 0.72rem; letter-spacing: 0.08em; color: var(--gris); }
</style>
