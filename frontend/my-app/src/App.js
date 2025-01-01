import React, { useState, useEffect } from 'react';
import ReactPaginate from "react-paginate";
import Swal from "sweetalert2";
import "./styles.css";


const itemSequence = [];

function App() {

  const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 1500
  })

  const itemsPerPage = 10;
  const [items, setItems] = useState([]);
  const [currentItems, setCurrentItems] = useState(null);
  const [pageCount, setPageCount] = useState(0);
  const [itemOffset, setItemOffset] = useState(0);

  const [recs, setRecs] = useState([]);


  function Items({ currentItems }) {
    
  
    const handleClick = (iid, description) => {
      if (iid) {
        itemSequence.push({"iid": iid, "description": description});
        Toast.fire({icon: "success", title: "Предмет добавлен!"});
      }
  
      const fetchRecs = async () => {
        const response = await fetch("http://localhost:8000/recommendation/personal", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({"uid": "test-user", "item_sequence": itemSequence})
        })
        const data = await response.json();
        try {          
          setRecs(data.recommendations);
          Toast.fire({icon: "success", title: "Рекомендации обновлены!"})
        }
        catch (error) {
          Toast.fire({icon: "erorr", title: error})
        }
      }
  
      fetchRecs();
    }
      return (
        <div className="item-grid">
        {currentItems && currentItems.map((item) => (
          <div className="item-card" onClick={() => handleClick(item.iid, item.description)}>
            <img src={item.image_url} alt={item.item_id} />
            <h4>{item.description}</h4>
          </div>
        ))}
        </div>
      );
  }

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await fetch("http://localhost:8000/recommendation/items");
        const data = await response.json();
        setItems(data);
        console.log('Items fetched:', data); // Добавьте этот лог для отладки
      } catch (error) {
        console.error("Error fetching items:", error);
      }
    };

    fetchItems();
  }, []);

  useEffect(() => {
    const endOffset = itemOffset + itemsPerPage;
    setCurrentItems(items.slice(itemOffset, endOffset));
    setPageCount(Math.ceil(items.length / itemsPerPage));
    console.log("current items", currentItems);
  }, [items, itemOffset, itemsPerPage]);

  const handlePageClick = (event) => {
    const newOffset = event.selected * itemsPerPage % items.length;
    setItemOffset(newOffset);
  };


  return (
    <div className="App">
      <p>
        Данное приложение предназначено для демонстрации работы рекомендательной системы.
      </p>
      <p>
        Когда происходит клик по карточке товара, имеется в виду, что пользователь совершил переход
        на страницу конкретного товара. Это может означать интерес к данному товару со стороны
        пользователя, который затем может привести к покупке или дальнейшему изучению информации о товаре.
      </p>
      <hr></hr>
      <Items currentItems={currentItems} />
      <ReactPaginate
        nextLabel=">"
        onPageChange={handlePageClick}
        pageRangeDisplayed={3}
        marginPagesDisplayed={2}
        pageCount={pageCount}
        previousLabel="<"
        pageClassName="page-item"
        pageLinkClassName="page-link"
        previousClassName="page-item"
        previousLinkClassName="page-link"
        nextClassName="page-item"
        nextLinkClassName="page-link"
        breakLabel="..."
        breakClassName="page-item"
        breakLinkClassName="page-link"
        containerClassName="pagination"
        activeClassName="active"
        renderOnZeroPageCount={null}
      />
      <hr></hr>
      <h1>Рекомендации</h1>
      <div className="item-grid">
        {recs.map((rec) => (
          <div className="item-card">
            <img src={rec.image_url} alt={rec.item_id} />
            <h4>{rec.description}</h4>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;