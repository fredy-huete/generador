import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { FileUp, CheckCircle, Download, Loader2 } from 'lucide-react'

type Status =
  | 'idle'
  | 'uploading'
  | 'uploaded'
  | 'processing'
  | 'processed'
  | 'downloaded'

function App() {
  const [status, setStatus] = useState<Status>('idle')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    if (!file.name.endsWith('.xlsx')) {
      alert('Please upload an Excel (.xlsx) file')
      return
    }

    try {
      setStatus('uploading')

      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('https://generador-alpha.vercel.app/', {
        method: 'POST',
        body: formData
      })

      setStatus('uploaded')

      if (!response.ok) throw new Error('Failed to process file')

      setStatus('processing')
      const blob = await response.blob()
      setStatus('processed')

      // Trigger download
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `processed-${file.name}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setStatus('downloaded')

      // Reset status after 3 seconds
      setTimeout(() => setStatus('idle'), 3000)
    } catch (error) {
      console.error('Error processing file:', error)
      alert('Error en el archivo. Intenta nuevamente.')
      setStatus('idle')
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': [
        '.xlsx'
      ]
    },
    multiple: false
  })

  const getStatusContent = () => {
    switch (status) {
      case 'idle':
        return (
          <>
            <FileUp className="w-20 h-20 mb-6 text-blue-500" />
            <p className="text-gray-600 text-lg">
              {isDragActive
                ? 'Drop the Excel file here'
                : 'Drag & drop an Excel file here, or click to select'}
            </p>
          </>
        )
      case 'uploading':
        return (
          <>
            <Loader2 className="w-20 h-20 mb-6 text-blue-500 animate-spin" />
            <p className="text-gray-600 text-lg">Uploading file...</p>
          </>
        )
      case 'uploaded':
        return (
          <>
            <CheckCircle className="w-20 h-20 mb-6 text-green-500" />
            <p className="text-gray-600 text-lg">File uploaded successfully!</p>
          </>
        )
      case 'processing':
        return (
          <>
            <Loader2 className="w-20 h-20 mb-6 text-blue-500 animate-spin" />
            <p className="text-gray-600 text-lg">Processing file...</p>
          </>
        )
      case 'processed':
        return (
          <>
            <CheckCircle className="w-20 h-20 mb-6 text-green-500" />
            <p className="text-gray-600 text-lg">File modified successfully!</p>
          </>
        )
      case 'downloaded':
        return (
          <>
            <Download className="w-20 h-20 mb-6 text-green-500" />
            <p className="text-gray-600 text-lg">File downloaded!</p>
          </>
        )
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-8 font-roboto text-gray-800">
        CREACIÓN DE NOMENCLATURA
      </h1>
      <div
        {...getRootProps()}
        className={`w-full max-w-2xl h-96 p-12 text-center bg-white rounded-xl shadow-lg transition-all duration-200 
          ${
            isDragActive
              ? 'border-2 border-blue-500 bg-blue-50'
              : 'border-2 border-dashed border-gray-300'
          }
          hover:border-blue-500 hover:bg-blue-50 cursor-pointer flex flex-col items-center justify-center`}
      >
        <input {...getInputProps()} />
        {getStatusContent()}
      </div>
    </div>
  )
}

export default App
