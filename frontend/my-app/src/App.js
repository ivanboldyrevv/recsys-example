import logo from './logo.svg';
import './App.css';

const handleSubmit = async () => {
  try {
    const response = await fetch('http://localhost:8000/recommendation/personal', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ uid: 'test-uid1', item_sequence: [{ iid: '22138', description: 'BAKING SET 9 PIECE RETROSPOT'}]})
    });
    
    if (!response.ok) {
      throw new Error(`Network response was not ok (${response.status})`);
    }
    
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error('There has been a problem with your fetch operation:', error);
  }
};

function MyButton() {
  handleSubmit();
  return (
    <button>I'm a button</button>
  );
}

export default function MyApp() {
  return (
    <div>
      <h1>Welcome to my app</h1>
      <MyButton />
    </div>
  );
}
// 
// {
  // "uid": "t-1-e-3-s-4-t",
  // "item_sequence": [
    // {
      // "iid": "22138",
      // "description": "BAKING SET 9 PIECE RETROSPOT"
    // },
    // {
      // "iid": "23254",
      // "description": "CHILDRENS CUTLERY DOLLY GIRL"
    // }
  // ]
// }