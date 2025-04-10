import express from 'express';
import multer from 'multer';
import { spawn } from 'child_process';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';  // Necesario para limpiar archivos temporales

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const upload = multer({ dest: 'uploads/' });

// Configuración de CORS
const corsOptions = {
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type'],
};
app.use(cors(corsOptions));

app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  // Obtener la ruta completa del archivo cargado
  const inputFilePath = path.join(__dirname, req.file.path);
  console.log('Input file path:', inputFilePath);

  let processedFilePath = '';
  // Ejecutar el script Python para procesar el archivo
  const pythonProcess = spawn('python', ['api/process-excel.py', inputFilePath]);

  // Capturar la salida estándar del script Python
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python output: ${data.toString()}`);
    processedFilePath = data.toString().trim();  // El nombre del archivo procesado
    console.log('Processed file path:', processedFilePath); // Imprimir la ruta completa del archivo procesado
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).send('Error processing file');
    }

    // Verificar si el archivo procesado existe y enviarlo
    if (fs.existsSync(processedFilePath)) {
      res.download(processedFilePath, (err) => {
        if (err) {
          console.error('Error sending file:', err);
        }
        // Limpiar archivos temporales
        fs.unlinkSync(req.file.path);  // Eliminar archivo original
        fs.unlinkSync(processedFilePath);  // Eliminar archivo procesado
      });
    } else {
      res.status(500).send('Error: El archivo procesado no se encuentra.');
    }
  });
});

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});