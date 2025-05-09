import React from 'react';
import './App.css';
import PrintJobsList from './components/PrintJobsList';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Sistema de Impresiones 3D</h1>
      </header>
      <main>
        <PrintJobsList />
      </main>
    </div>
  );
}

export default App;
