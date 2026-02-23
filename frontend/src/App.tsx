import { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    axios
      .get("http://localhost:5001/api/hello")
      .then((res) => setMessage(res.data.message))
      .catch((err) => console.error("Error fetching /api/hello:", err));
  }, []);

  return (
    <h1>{message}</h1>
  );
}

export default App;
