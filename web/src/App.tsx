import { Link, Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import { Emulator } from './emulator/Emulator'

function App() {
  return (
    <>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/emulator">Emulator</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/emulator" element={<Emulator />} />
      </Routes>
    </>
  )
}

export default App
