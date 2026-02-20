import { useState } from 'react'
import './App.css'

function App() {
  const [formData, setFormData] = useState({
    edad: 22,
    peso: 70,
    estatura: 175,
    genero: 'masculino',
    objetivo: 'subir_masa',
    nivel: 'principiante',
    dias_disponibles: 3,
    equipo_disponible: ['barbell', 'dumbbell']
  })

  const [rutina, setRutina] = useState(null)

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value})
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('http://localhost:8000/generar-rutina', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      const data = await response.json()
      setRutina(data)
    } catch (error) {
      console.error("Error conectando con el backend:", error)
    }
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>Sistema Experto de Gym 💪</h1>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '300px' }}>
        <label>Nivel:
          <select name="nivel" onChange={handleChange}>
            <option value="principiante">Principiante</option>
            <option value="intermedio">Intermedio</option>
          </select>
        </label>

        <label>Días disponibles:
          <input type="number" name="dias_disponibles" value={formData.dias_disponibles} onChange={handleChange} />
        </label>

        <button type="submit" style={{ padding: '10px', background: '#007bff', color: 'white', border: 'none' }}>
          Generar Rutina
        </button>
      </form>

      {rutina && rutina.ejercicios_recomendados && (
        <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px' }}>
          <h2>Tu Plan: {rutina.tipo_rutina}</h2>
          <p>{rutina.mensaje}</p>
          <ul>
                {rutina.ejercicios_recomendados && rutina.ejercicios_recomendados.map((ej, index) => (
                  <li key={index} style={{ marginBottom: '10px' }}>
                    <strong>{ej.name.toUpperCase()}</strong> <br/>
                    <small>Músculo: {ej.target} | Equipo: {ej.equipment}</small>
                  </li>
                ))}
              </ul>
        </div>
      )}
    </div>
  )
}

export default App