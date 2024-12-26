import React, { useState, useEffect } from 'react';
import PaginatedItems from './ItemPaginate';

function App() {

  return (
    <div className="App">
      <PaginatedItems itemsPerPage={10} />
      <hr></hr>
      <h1>Рекомендации</h1>
    </div>
  );
}

export default App;