import express from 'express'
import multer from 'multer'
import { spawn } from 'child_process'
import cors from 'cors'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs' // Necesario para limpiar archivos temporales

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()
const upload = multer({ dest: 'uploads/' })

// app.use(cors());

// app.use(cors({
//   origin: 'http://localhost:5173'
//   //origin: '*', // Dirección del frontend
//  // Permitir el envío de cookies
// }));

app.use(
  cors({
    origin: 'https://generador-nu.vercel.app'
  })
)

// const corsOptions = {
//   origin: '*',
//   methods: ['GET', 'POST', 'PUT', 'DELETE'],
//   allowedHeaders: ['Content-Type'],
// };

// app.use(cors(corsOptions));

app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.')
  }

  // Obtener la ruta completa del archivo
  const inputFilePath = path.join(__dirname, req.file.path)

  // Procesar el archivo usando el script de Python
  const pythonProcess = spawn('python', ['api/process-excel.py', inputFilePath])

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python output: ${data}`)
  })

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python error: ${data}`)
  })

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).send('Error processing file')
    }

    // Construir la ruta del archivo procesado
    const processedFilePath = inputFilePath + '_processed.xlsx'

    // Verificar si el archivo procesado existe y enviarlo
    if (fs.existsSync(processedFilePath)) {
      res.download(processedFilePath, (err) => {
        if (err) {
          console.error('Error sending file:', err)
        }
        // Limpiar archivos temporales
        fs.unlinkSync(req.file.path) // Eliminar archivo original
        fs.unlinkSync(processedFilePath) // Eliminar archivo procesado
      })
    } else {
      res.status(500).send('Error: El archivo procesado no se encuentra.')
    }
  })
})

const PORT = 5000
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})
